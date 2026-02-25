"""
Arabic Mental Health Twitter Collector — delusional_disorder (#2/21)
==========================================================
Collects tweets containing Arabic self-disclosure of mental health conditions.

v4 — Unified Twitter+Reddit methodology (built on v3-3 skeleton)
  All NLP, keywords, and phrases ported from Reddit collector (Feb 18).
  Login, cookies, rate limits, and timing preserved from v3-3.

  New in v4 (from Reddit):
  - 21 diagnoses (from 10) — DSM-5 / ICD-11 clinically reviewed
  - Discovery/confirmation disclosure phrases (طلع تشخيصي, اكتشفت إن عندي, etc.)
  - Arabic word-boundary checks (لدي, معي, فيني, جاني false-positive prevention)
  - Grammar-aware Stage 2 matching (connector-type-aware proximity)
  - Medication detection (305 terms, Arabic+English, compiled regex)
  - Comorbidity analysis (--comorbidity flag)
  - Expanded FEMININE_KEYWORDS for all 21 diagnoses
  - Grammar validation safety nets (بعلى, بأنا, etc.)
  - Proximity distance: 40 characters (from 20)

  New in v4 (Twitter-specific):
  - Retweet filtering (server-side + client-side)
  - 'all' mode (run all 21 conditions + unified CSV)
  - Progress saving every 50 queries
  - Consecutive 404 abort with re-login instructions
  - ETA tracking
  - CSV output (not Excel)
  - Extra metadata: user_location, statuses_count, profile_url, tweet_url

  Preserved from v3-3:
  - Login via twikit Client + cookies.json
  - Rate limit handling (15-min wait on 429)
  - Batch delays (3-6s), phrase delays (8-12s)
  - Forward-only 40-char grammar-aware proximity matching
  - Google Drive integration

Setup:
    pip install twikit pandas

Usage:
    python arabic_mental_health_twitter_v4.py schizophrenia
    python arabic_mental_health_twitter_v4.py depression --max-batches 5
    python arabic_mental_health_twitter_v4.py all
    python arabic_mental_health_twitter_v4.py all --comorbidity
    python arabic_mental_health_twitter_v4.py --list-diagnoses
    python arabic_mental_health_twitter_v4.py depression --list-phrases
    python arabic_mental_health_twitter_v4.py --comorbidity
"""

from twikit import Client, TooManyRequests
import asyncio
from datetime import datetime, timezone
import pandas as pd
from random import randint
import re
import os
import glob
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Set, Iterator
from pathlib import Path
from collections import Counter
from functools import lru_cache

# ============================================================
# GOOGLE DRIVE INTEGRATION
# ============================================================

GDRIVE_ENABLED = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GDRIVE_ENABLED = True
except ImportError:
    pass

GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']


def setup_gdrive_credentials():
    """Set up Google Drive credentials."""
    if not GDRIVE_ENABLED:
        print("❌ Google Drive libraries not installed.")
        print("   Run: pip install google-auth-oauthlib google-api-python-client")
        return None
    
    creds = None
    token_path = Path('gdrive_token.json')
    creds_path = Path('credentials.json')
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GDRIVE_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print("❌ credentials.json not found.")
                print("   Download from Google Cloud Console:")
                print("   https://console.cloud.google.com/apis/credentials")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), GDRIVE_SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def upload_to_gdrive(filepath: str, folder_id: str = None) -> Optional[str]:
    """Upload a file to Google Drive."""
    if not GDRIVE_ENABLED:
        print("⚠️  Google Drive not enabled. File saved locally only.")
        return None
    
    creds = setup_gdrive_credentials()
    if not creds:
        return None
    
    try:
        service = build('drive', 'v3', credentials=creds)
        filename = os.path.basename(filepath)
        
        mime_types = {
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.txt': 'text/plain',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        ext = os.path.splitext(filepath)[1].lower()
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        file_metadata = {'name': filename}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(filepath, mimetype=mime_type)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_url = file.get('webViewLink')
        print(f"✅ Uploaded to Google Drive: {file_url}")
        return file_url
        
    except Exception as e:
        print(f"❌ Google Drive upload failed: {e}")
        return None


# ============================================================
# CONFIGURATION
# ============================================================

PROXIMITY_DISTANCE = 40

# ============================================================
# FOLDER CONFIGURATION (Google Drive / Colab integration)
# ============================================================

if os.path.exists("/content/drive/MyDrive"):
    INPUT_FOLDER = "/content/drive/MyDrive/Twitter_Mental_Health-delusional_disorder/input"
    OUTPUT_FOLDER = "/content/drive/MyDrive/Twitter_Mental_Health-delusional_disorder"
else:
    INPUT_FOLDER = "./input"
    OUTPUT_FOLDER = "./output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(INPUT_FOLDER, exist_ok=True)
print(f"📂 Input folder:  {INPUT_FOLDER}")
print(f"📂 Output folder: {OUTPUT_FOLDER}")


@dataclass
class DiagnosisConfig:
    """Configuration for a mental health diagnosis."""
    name: str
    name_ar: str
    keywords: List[str] = field(default_factory=list)
    keywords_restricted: List[str] = field(default_factory=list)


# ╔══════════════════════════════════════════════════════════════╗
# ║  UNIVERSAL DIAGNOSIS PHRASES (from Reddit v3.1)             ║
# ╚══════════════════════════════════════════════════════════════╝

DIAGNOSIS_PHRASES = [
    # === مصاب MASCULINE (with أنا) ===
    'كشخص مصاب', 'انا مصاب', 'أنا مصاب',
    # === مصابة/مصابه FEMININE (with أنا) ===
    'انا مصابة', 'أنا مصابة',
    'انا مصابه', 'أنا مصابه',

    # === اعاني من (both hamza variants) ===
    'انا اعاني من', 'أنا أعاني من', 'انا أعاني من', 'أنا اعاني من',
    'اعاني من', 'أعاني من',

    # === مريض MASCULINE (with أنا) ===
    'انا مريض', 'أنا مريض',
    # === مريضة/مريضه FEMININE (with أنا) ===
    'انا مريضة', 'أنا مريضة',
    'انا مريضه', 'أنا مريضه',

    # === عندي (with أنا variants) ===
    'عندي', 'أنا عندي', 'انا عندي',

    # === تشخيص phrases ===
    'تم تشخيصي', 'شخصوني', 'شخصني', 'شخصتني', 'شخصت',

    # === Doctor phrases (BOTH masculine and feminine) ===
    'شخصني الطبيب', 'شخصني الدكتور',
    'شخصتني الطبيبة', 'شخصتني الطبيبه',
    'شخصتني الدكتورة', 'شخصتني الدكتوره',

    # === Specialist phrases ===
    'الاخصائي شخصني', 'الأخصائي شخصني',
    'الاخصائية شخصتني', 'الأخصائية شخصتني',
    'الاخصائيه شخصتني', 'الأخصائيه شخصتني',

    # === اعيش مع ===
    'انا اعيش مع', 'أنا أعيش مع',

    # === اصبت ===
    'اصبت', 'أصبت',

    # === أتعالج من ===
    'انا أتعالج من', 'أنا أتعالج من', 'انا اتعالج من', 'أنا اتعالج من',

    # === v3 ADDITIONS: Discovery/confirmation phrases ===
    'تشخيصي هو', 'طلع تشخيصي',
    'تشخيصي كان', 'طلع تشخيصي هو',
    'طلعت مصاب', 'طلعت مصابة', 'طلعت مصابه',
    'طلعت عندي', 'طلع عندي',
    'لقيت نفسي مصاب', 'لقيت نفسي مصابة', 'لقيت نفسي مصابه',
    'لقيت نفسي عندي',
    'اكتشفت إن عندي', 'اكتشفت ان عندي',
    'اكتشفت إني مصاب', 'اكتشفت اني مصاب',
    'اكتشفت إني مصابة', 'اكتشفت اني مصابة',
    'عرفت إني عندي', 'عرفت اني عندي',
    'عرفت إن أنا مصاب', 'عرفت ان أنا مصاب',
    'عرفت إن أنا مصابة', 'عرفت ان أنا مصابة',
    'اتأكدت إن عندي', 'اتأكدت ان عندي',
    'اتأكدت إني مصاب', 'اتأكدت اني مصاب',
    'اتأكدت إني مصابة', 'اتأكدت اني مصابة',
    'بعد التشخيص طلع عندي',
    'التحليل أثبت إن عندي', 'التحليل اثبت ان عندي',

    # === v3.1 ADDITIONS ===
    'كنت مصاب', 'كنت مصابة', 'كنت مصابه',
    'أكد الطبيب إصابتي', 'أكد الدكتور إصابتي',
    'الدكتور أكد إصابتي', 'الطبيب أكد إصابتي',
    'تم التأكيد على إصابتي', 'تم إثبات إصابتي',
    'الدكتور أكد التشخيص', 'الطبيب أكد التشخيص',
    'الدكتور أثبت التشخيص', 'الطبيب أثبت التشخيص',
    'تشخيص الطبيب هو', 'تشخيص الدكتور هو',
    'تشخيص الطبيب كان', 'تشخيص الدكتور كان',
    'تشخيص المرض كان', 'تشخيص المرض هو',
    'تشخيص حالتي يبين', 'تشخيص حالتي هو', 'تشخيص حالتي كان',
    'تشخيص الحالة كان', 'تشخيص الحالة هو',
    'تم تشخيص حالتي على أنها',
    'التشخيص الذي حصلت عليه هو',
    'طلع إن التشخيص هو', 'طلع ان التشخيص هو',
    'اتضح إن التشخيص كان', 'اتضح ان التشخيص كان',
    'اتضح إن التشخيص هو', 'اتضح ان التشخيص هو',
    'أنا بواجه مشكلة اسمها', 'انا بواجه مشكلة اسمها',
    'أنا بأواجه مشكلة اسمها', 'انا بأواجه مشكلة اسمها',
]


# ╔══════════════════════════════════════════════════════════════╗
# ║  CULTURAL/DIALECT PHRASES (from Reddit v3)                  ║
# ╚══════════════════════════════════════════════════════════════╝

CULTURAL_PHRASES = {
    "gulf": [
        'انا مصاب', 'أنا مصاب', 'عندي', 'فيني',
        'انا معايش', 'انا معايشة', 'انا معايشه',
        'اعاني من',
        'ابتليت', 'مبتلي', 'مبتلية', 'مبتليه',
        'الله ابتلاني',
        'جاني', 'جاتني',
    ],
    "levantine": [
        'انا مصاب', 'أنا مصاب', 'عندي', 'معي',
        'بعاني من', 'عم بعاني',
        'صار معي', 'صارت معي',
        'اجاني', 'اجاتني',
        'طلعلي', 'طلعتلي',
    ],
    "egyptian": [
        'انا مصاب', 'أنا مصاب', 'عندي', 'معايا',
        'بعاني من',
        'جالي', 'جاتلي',
        'طلعلي', 'طلعتلي',
        'اتشخصت',
        # v3 ADDITIONS: Egyptian discovery/confirmation
        'لقيت نفسي عندي', 'لقيت نفسي مصاب',
        'طلعت عندي', 'طلعت مصاب',
        'عرفت إني عندي', 'عرفت اني عندي',
        'اكتشفت إن عندي', 'اكتشفت ان عندي',
        'اتأكدت إن عندي', 'اتأكدت ان عندي',
    ],
    "maghrebi": [
        'انا مصاب', 'عندي', 'كاين عندي',
        'جاني', 'جاتني',
        'طلعلي', 'طلعتلي',
        'تشخصت',
    ],
    "msa": [
        'أنا مصاب', 'أنا مصابة', 'أنا مصابه',
        'لدي', 'أعاني من',
        'تم تشخيصي',
        'شُخِّصت', 'شخصت',
        'أتعايش مع', 'اتعايش مع',
        'أصبت',
        'مريض', 'مريضة', 'مريضه',
        # v3 ADDITIONS: MSA formal discovery
        'تشخيصي هو', 'طلع تشخيصي',
    ],
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  21 DIAGNOSES WITH KEYWORDS — DSM-5 / ICD-11 Reviewed      ║
# ╚══════════════════════════════════════════════════════════════╝

DIAGNOSES = {

    # ── 1. Schizophrenia Spectrum ──
    "schizophrenia": DiagnosisConfig(
        name="schizophrenia",
        name_ar="الفصام",
        keywords=[
            'فصام', 'الفصام',
            'شيزوفرينيا', 'الشيزوفرينيا',
            'اضطراب الفصام',
            'انفصام الشخصية', 'انفصام الشخصيه',
            'فصام الشخصية', 'فصام الشخصيه',
            'أنفصام الشخصية',
            'اضطراب ذهاني',
            'psychotic disorder',
            'schizophrenia',
            'الاضطراب الفصامي الوجداني',
            'الاضطراب الفصامي العاطفي',
            'فصام وجداني', 'فصام عاطفي',
            'اضطراب فصامي وجداني',
            'سكيزوأفكتيف', 'سكيزو افيكتيف',
            'schizoaffective disorder', 'schizoaffective',
        ],
    ),

    # ── 2. Delusional Disorder ──
    "delusional_disorder": DiagnosisConfig(
        name="delusional_disorder",
        name_ar="الاضطراب الوهمي",
        keywords=[
            'الاضطراب الوهمي', 'اضطراب وهمي',
            'الاضطراب الضلالي', 'اضطراب ضلالي',
            'الاضطراب الوهامي',
            'اضطراب الأوهام', 'اضطراب الاوهام',
            'أوهام مرضية',
            'delusional disorder', 'delusional disorder NOS',
        ],
    ),

    # ── 3. Bipolar and Related Disorders ──
    "bipolar": DiagnosisConfig(
        name="bipolar",
        name_ar="ثنائي القطب",
        keywords=[
            'ثنائي القطب', 'اضطراب ثنائي القطب',
            'bipolar', 'bipolar disorder',
            'بايبولار', 'بايبولر',
            'manic-depressive illness',
            'ثنائي القطب النوع الأول', 'ثنائي القطب النوع الاول',
            'ثنائي القطب النوع الثاني',
            'bipolar I', 'bipolar II', 'bipolar 1', 'bipolar 2',
            'بايبولار 1', 'بايبولار 2',
            'هوس خفيف', 'الهوس الخفيف',
            'نوبة هوسية', 'نوبات هوسية',
            'نوبة مانيا', 'نوبات مانيا',
            'مانيا',
            'hypomania', 'mania', 'manic episode',
            'سيكلوثيميا', 'سيكلوثيمية',
            'الاضطراب الدوري', 'اضطراب دوري',
            'cyclothymia', 'cyclothymic disorder',
        ],
    ),

    # ── 4. Depressive Disorders ──
    "depression": DiagnosisConfig(
        name="depression",
        name_ar="الاكتئاب",
        keywords=[
            'اكتئاب', 'الاكتئاب', 'الإكتئاب', 'إكتئاب',
            'depression',
            'ديبريشن', 'دبرشن', 'ديبرشن',
            'الاضطراب الاكتئابي الجسيم', 'اضطراب اكتئابي جسيم',
            'نوبة اكتئاب جسيم', 'نوبة الاكتئاب الجسيم',
            'اكتئاب حاد', 'اكتئاب شديد', 'اكتئاب مزمن', 'اكتئاب متوسط',
            'الاضطراب الاكتئابي', 'اضطراب اكتئابي',
            'الاكتئاب السريري', 'اكتئاب سريري',
            'الاكتئاب الحاد', 'الاكتئاب الشديد',
            'اضطراب الاكتئاب الرئيسي', 'الاكتئاب الرئيسي',
            'أكتئاب', 'أكتئاب حاد', 'أكتئاب شديد',
            'أكتئاب متوسط', 'أكتئاب مزمن', 'أكتئاب سريري',
            'اكتأب', 'اكتاب',
            'major depressive disorder', 'clinical depression',
            'depressive disorder', 'MDD',
            'persistent depressive disorder', 'dysthymia',
            'الاكتئاب المستمر', 'اضطراب الاكتئاب المستمر',
            'اضطراب اكتئابي مستمر',
            'سوء المزاج',
            'دسثيميا', 'دايسثيميا',
            'اكتئاب ما بعد الولادة',
            'اكتئاب النفاس', 'اكتئاب نفاس',
            'الاكتئاب النفاسي',
            'الاكتئاب ما بعد الولادة', 'اكتئاب بعد الولادة',
            'postpartum depression', 'postnatal depression', 'PPD',
            'الاكتئاب الموسمي', 'اكتئاب موسمي',
            'seasonal affective disorder', 'SAD',
            'الاكتئاب الذهاني', 'اكتئاب ذهاني',
            'psychotic depression',
        ],
    ),

    # ── 5. Anxiety Disorders ──
    "anxiety": DiagnosisConfig(
        name="anxiety",
        name_ar="اضطراب القلق",
        keywords=[
            'اضطراب القلق', 'اضطراب قلق',
            'قلق عام', 'القلق العام',
            'قلق مرضي', 'القلق المرضي',
            'قلق مزمن', 'القلق المزمن',
            'GAD', 'gad',
            'anxiety disorder', 'generalized anxiety disorder', 'generalized anxiety',
            'اضطراب قلق عام',
            'رهاب اجتماعي', 'الرهاب الاجتماعي',
            'قلق اجتماعي', 'القلق الاجتماعي',
            'اضطراب القلق الاجتماعي',
            'social anxiety disorder', 'social anxiety',
            'الخوف المرضي', 'خوف مرضي',
            'رهاب محدد', 'الرهاب المحدد',
            'specific phobia',
            'رهاب الخلاء', 'رهاب الأماكن المفتوحة',
            'رهاب الأماكن العامة',
            'agoraphobia',
            'قلق الانفصال', 'اضطراب قلق الانفصال',
            'قلق الفراق',
            'separation anxiety disorder',
        ],
    ),

    # ── 6. Panic Disorder ──
    "panic": DiagnosisConfig(
        name="panic",
        name_ar="اضطراب الهلع",
        keywords=[
            'نوبة هلع', 'نوبه هلع',
            'نوبات هلع', 'نوبات الهلع',
            'الهلع',
            'اضطراب الهلع',
            'panic attack', 'panic attacks', 'panic disorder',
            'نوبة ذعر', 'نوبه ذعر',
            'نوبات الذعر',
            'الذعر المرضي',
        ],
    ),

    # ── 7. OCD and Related Disorders ──
    "ocd": DiagnosisConfig(
        name="ocd",
        name_ar="الوسواس القهري",
        keywords=[
            'وسواس قهري', 'الوسواس القهري',
            'اضطراب الوسواس القهري',
            'اضطراب وسواسي قهري', 'الاضطراب الوسواسي القهري',
            'OCD', 'ocd',
            'obsessive-compulsive disorder', 'obsessive disorder',
            'افكار وسواسية', 'أفكار وسواسية',
            'افكار وسواسيه', 'أفكار وسواسيه',
            'افعال قهرية', 'أفعال قهرية',
            'افعال قهريه', 'أفعال قهريه',
            'سلوك قهري',
            'الوسواس الديني', 'وسواس ديني',
            'الوسواس الشرعي', 'وسواس شرعي',
            'وسواس الصلاة', 'وسواس الوضوء',
            'وسواس الطهارة', 'وسواس الطهاره',
            'وسواس النجاسة', 'وسواس النجاسه',
            'الوسواس في العبادة', 'وسواس في العباده',
            'وسواس الحلال والحرام',
            'religious OCD', 'scrupulosity',
            'اضطراب تشوه الجسم', 'اضطراب تشوه الجسد',
            'تشوه الجسم', 'تشوه الجسد',
            'ديسمورفيا', 'ديسمورفوبيا',
            'body dysmorphic disorder', 'BDD', 'body dysmorphia',
            'اكتناز مرضي', 'الاكتناز المرضي',
            'اضطراب الاكتناز', 'اضطراب التخزين المرضي',
            'hoarding disorder', 'compulsive hoarding',
        ],
    ),

    # ── 8. Trauma and Stressor-Related Disorders ──
    "ptsd": DiagnosisConfig(
        name="ptsd",
        name_ar="اضطراب ما بعد الصدمة",
        keywords=[
            'اضطراب ما بعد الصدمة', 'اضطراب ما بعد الصدمه',
            'ما بعد الصدمة', 'ما بعد الصدمه',
            'كرب ما بعد الصدمة', 'كرب ما بعد الصدمه',
            'PTSD', 'ptsd',
            'post-traumatic stress disorder',
            'صدمة نفسية', 'صدمه نفسيه',
            'صدمات نفسية', 'صدمات نفسيه',
            'بي تي إس دي', 'بي تي اس دي',
            'اضطراب الإجهاد الحاد', 'اضطراب الاجهاد الحاد',
            'acute stress disorder',
            'صدمة معقدة', 'الصدمة المعقدة',
            'اضطراب ما بعد الصدمة المعقد',
            'complex PTSD', 'C-PTSD', 'CPTSD',
        ],
    ),

    # ── 9. Feeding and Eating Disorders ──
    "eating_disorder": DiagnosisConfig(
        name="eating_disorder",
        name_ar="اضطراب الأكل",
        keywords=[
            'اضطراب الأكل', 'اضطراب أكل',
            'اضطراب الاكل', 'اضطراب اكل',
            'eating disorder',
            'فقدان الشهية العصبي', 'فقدان الشهيه العصبي',
            'فقدان الشهية', 'فقدان الشهيه',
            'أنوركسيا', 'انوركسيا',
            'anorexia nervosa', 'anorexia',
            'الشره المرضي العصبي', 'شره مرضي عصبي',
            'شره عصبي', 'الشره العصبي',
            'بوليميا',
            'bulimia nervosa', 'bulimia',
            'اضطراب نهم الطعام', 'نهم الطعام', 'نهم طعام',
            'الأكل القهري', 'اكل قهري',
            'binge-eating disorder', 'binge eating disorder', 'BED',
            'اضطراب الطعام الانتقائي', 'طعام انتقائي',
            'selective eating disorder',
            'اضطراب تجنب الطعام التقييدي',
            'اضطراب تجنب وتقييد تناول الطعام',
            'ARFID',
            'avoidant restrictive food intake disorder',
            'أورثوريكسيا', 'اورثوريكسيا',
            'orthorexia', 'orthorexia nervosa',
        ],
    ),

    # ── 10. ADHD ──
    "adhd": DiagnosisConfig(
        name="adhd",
        name_ar="فرط الحركة وتشتت الانتباه",
        keywords=[
            'ADHD', 'adhd',
            'فرط حركة', 'فرط حركه',
            'فرط الحركة', 'فرط الحركه',
            'اضطراب فرط الحركة', 'اضطراب فرط الحركه',
            'تشتت انتباه', 'تشتت الانتباه', 'نقص الانتباه',
            'اي دي اتش دي', 'إيه دي إتش دي', 'ايه دي اتش دي',
            'اضطراب فرط الحركه وتشتت الانتباه',
            'فرط الحركه وتشتت الانتباه',
            'فرط الحركة وتشتت الانتباه',
            'attention deficit hyperactivity disorder',
            'attention deficit disorder',
            'اضطراب الانتباه', 'اضطراب نقص الانتباه',
            'نقص انتباه',
        ],
        keywords_restricted=[
            'ADD', 'add',
        ],
    ),

    # ── 11. Autism ──
    "autism": DiagnosisConfig(
        name="autism",
        name_ar="التوحد",
        keywords=[
            'التوحد', 'توحد',
            'اضطراب طيف التوحد', 'طيف التوحد',
            'autism', 'autism spectrum disorder',
            'طيف توحد',
            'أسبرجر', 'اسبرجر',
            'متلازمة أسبرجر', 'متلازمة اسبرجر',
            'متلازمه أسبرجر', 'متلازمه اسبرجر',
            "Asperger's", 'Asperger', 'aspergers',
            'asperger syndrome', "asperger's syndrome",
        ],
    ),

    # ── 12. Dissociative Disorders ──
    "did": DiagnosisConfig(
        name="did",
        name_ar="اضطراب الهوية التفارقي",
        keywords=[
            'اضطراب الهوية التفارقي', 'اضطراب الهويه التفارقي',
            'هوية تفارقية', 'هويه تفارقيه',
            'الهوية التفارقية',
            'dissociative identity disorder', 'DID',
            'multiple personality disorder',
            'اضطراب تعدد الشخصيات', 'تعدد الشخصيات',
        ],
    ),

    # ── 13. Sleep-Wake Disorders ──
    "sleep_disorder": DiagnosisConfig(
        name="sleep_disorder",
        name_ar="اضطراب النوم",
        keywords=[
            'الأرق', 'أرق', 'الارق', 'ارق',
            'insomnia', 'chronic insomnia',
            'اضطراب الأرق', 'اضطراب الارق',
            'اضطراب النوم', 'sleep disorder',
            'انقطاع النفس النومي', 'انقطاع النفس أثناء النوم',
            'sleep apnea',
            'فرط النوم', 'فرط نوم', 'hypersomnia',
            'الخدار', 'خدار', 'narcolepsy',
        ],
    ),

    # ── 14. Trichotillomania / BFRB ──
    "trichotillomania": DiagnosisConfig(
        name="trichotillomania",
        name_ar="اضطراب شد الشعر",
        keywords=[
            'اضطراب شد الشعر', 'شد الشعر',
            'نتف الشعر', 'اقتلاع الشعر',
            'trichotillomania', 'hair-pulling disorder',
            'اضطراب نتف الجلد', 'نتف الجلد',
            'جرح الجلد المرضي',
            'excoriation disorder', 'skin-picking disorder',
            'اضطراب قضم الأظافر', 'قضم الأظافر',
            'nail-biting disorder', 'onychophagia',
        ],
    ),

    # ── 15. Personality Disorders ──
    "bpd": DiagnosisConfig(
        name="bpd",
        name_ar="اضطراب الشخصية الحدية",
        keywords=[
            'اضطراب الشخصية الحدية', 'اضطراب الشخصيه الحديه',
            'الشخصيه الحدية', 'الشخصية الحدية', 'الشخصيه الحديه',
            'اضطراب الحدية', 'اضطراب الحديه',
            'الحدية', 'الحديه',
            'بوردرلاين', 'البوردرلاين',
            'BPD', 'bpd', 'borderline',
            'borderline personality disorder',
        ],
    ),

    "narcissistic_pd": DiagnosisConfig(
        name="narcissistic_pd",
        name_ar="اضطراب الشخصية النرجسية",
        keywords=[
            'اضطراب الشخصية النرجسية', 'اضطراب الشخصيه النرجسيه',
            'الشخصية النرجسية', 'الشخصيه النرجسيه',
            'narcissistic personality disorder', 'NPD', 'npd',
            'نرجسية مرضية', 'نرجسيه مرضيه',
        ],
    ),

    "avoidant_pd": DiagnosisConfig(
        name="avoidant_pd",
        name_ar="اضطراب الشخصية التجنبية",
        keywords=[
            'اضطراب الشخصية التجنبية', 'اضطراب الشخصيه التجنبيه',
            'الشخصية التجنبية', 'الشخصيه التجنبيه',
            'اضطراب الشخصية الانعزالية', 'اضطراب الشخصيه الانعزاليه',
            'الشخصية الانعزالية', 'الشخصيه الانعزاليه',
            'avoidant personality disorder', 'AvPD',
        ],
    ),

    "schizoid_pd": DiagnosisConfig(
        name="schizoid_pd",
        name_ar="اضطراب الشخصية الفصامية",
        keywords=[
            'اضطراب الشخصية الفصامية', 'اضطراب الشخصيه الفصاميه',
            'الشخصية الفصامية', 'الشخصيه الفصاميه',
            'الشخصية المنعزلة',
            'schizoid personality disorder', 'schizoid PD',
        ],
    ),

    "schizotypal_pd": DiagnosisConfig(
        name="schizotypal_pd",
        name_ar="اضطراب الشخصية الفصامية النمطية",
        keywords=[
            'اضطراب الشخصية الفصامية النمطية',
            'الشخصية الفصامية النمطية',
            'سكيزوتايبال',
            'schizotypal personality disorder', 'schizotypal PD',
        ],
    ),

    "paranoid_pd": DiagnosisConfig(
        name="paranoid_pd",
        name_ar="اضطراب الشخصية الزوراني",
        keywords=[
            'اضطراب الشخصية الزوراني', 'اضطراب الشخصية الزورانية',
            'اضطراب الشخصيه الزوراني', 'اضطراب الشخصيه الزورانيه',
            'الشخصية الزورانية', 'الشخصيه الزورانيه',
            'اضطراب الشخصية البارانوية', 'اضطراب الشخصيه البارانويه',
            'الشخصية البارانوية', 'الشخصيه البارانويه',
            'البارانويا', 'بارانويا',
            'الشخصية الارتيابية', 'الشخصيه الارتيابيه',
            'اضطراب الشخصية الارتيابية',
            'اضطراب جنون الارتياب', 'جنون الارتياب',
            'paranoid personality disorder',
        ],
    ),

    # ── 16. Suicidal Ideation ──
    "suicidal": DiagnosisConfig(
        name="suicidal",
        name_ar="الأفكار الانتحارية",
        keywords=[
            'افكار انتحارية', 'أفكار انتحارية',
            'افكار انتحاريه', 'أفكار انتحاريه',
            'الفكر الانتحاري',
            'فكر انتحاري',
            'suicidal thoughts', 'suicidal ideation', 'suicidal tendencies',
        ],
        keywords_restricted=[
            'انتحار', 'الانتحار', 'رغبة بالانتحار',
            'أنتحار',
            'ايذاء نفس', 'إيذاء نفس',
            'ايذاء النفس', 'إيذاء النفس',
            'جرح النفس', 'جروح النفس',
            'ميل للانتحار',
            'محاولة انتحار', 'محاوله انتحار', 'محاولات الانتحار',
            'suicide attempts', 'suicide attempt',
            'self-harm', 'self-injury', 'cutting',
        ],
    ),
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  FEMININE NOUNS — expanded for all 21 diagnoses             ║
# ╚══════════════════════════════════════════════════════════════╝

FEMININE_KEYWORDS = {
    # Panic
    'نوبة هلع', 'نوبه هلع', 'نوبة ذعر', 'نوبه ذعر',
    'نوبات هلع', 'نوبات الذعر',
    # PTSD
    'صدمة نفسية', 'صدمه نفسيه',
    'صدمات نفسية', 'صدمات نفسيه',
    # BPD / Personality
    'الشخصية الحدية', 'الشخصيه الحديه',
    'الشخصية النرجسية', 'الشخصيه النرجسيه',
    'الشخصية الانعزالية', 'الشخصيه الانعزاليه',
    'الشخصية الانطوائية', 'الشخصيه الانطوائيه',
    # Suicidal
    'افكار انتحارية', 'أفكار انتحارية', 'افكار انتحاريه', 'أفكار انتحاريه',
    # OCD
    'افكار وسواسية', 'أفكار وسواسية', 'افكار وسواسيه', 'أفكار وسواسيه',
    'الأفعال القهرية', 'الأفعال القهريه', 'الافعال القهرية', 'الافعال القهريه',
    # Schizophrenia
    'الشيزوفرينيا', 'شيزوفرينيا',
    'انفصام الشخصية', 'انفصام الشخصيه',
    # Eating disorders
    'فقدان الشهية', 'فقدان الشهيه',
    'فقدان الشهية العصبي', 'فقدان الشهيه العصبي',
    # DID
    'هوية تفارقية', 'هويه تفارقيه',
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  MEDICATION KEYWORDS (305 terms)                            ║
# ╚══════════════════════════════════════════════════════════════╝

MEDICATION_KEYWORDS = [
    # === ARABIC NAMES (with hamza أ) ===
    'أبيليفاي', 'أتوموكسيتين', 'أتيفان', 'أريبيبرازول', 'ألبرازولام', 'أميتريبتيلين',
    'أنافرانيل', 'أولانزابين', 'أوكسكاربازيبين', 'أسينابين', 'أغوميلاتين', 'أكامبروسيت',
    'إسيتالوبرام', 'إفكسور', 'إنفيغا', 'إيزوبيكلون', 'إيميبرامين',
    # === ARABIC NAMES (without hamza ا) ===
    'ابيليفاي', 'اتوموكسيتين', 'اتيفان', 'اريبيبرازول', 'افكسور', 'اميتريبتيلين',
    'انافرانيل', 'انفيغا', 'اولانزابين', 'ايزوبيكلون', 'ايميبرامين', 'اسينابين',
    'اغوميلاتين', 'اوكسكاربازيبين', 'اكامبروسيت',
    # === ARABIC - ب ===
    'باروكستين', 'باروكسيتين', 'باليبيريدون', 'برازوسين', 'بروبرانولول', 'بروزاك',
    'بريجابالين', 'بريستيك', 'بوبروبيون', 'بوسبيرون', 'برومازيبام', 'بريكسبيبرازول',
    'بوبرينورفين', 'بيرفينازين',
    # === ARABIC - ت ===
    'ترازودون', 'تربتيزول', 'توبيراميت', 'تيجريتول', 'توفرانيل', 'تريلبتال', 'ترينتليكس',
    # === ARABIC - ج ===
    'جابابنتين',
    # === ARABIC - د ===
    'دولوكستين', 'ديازيبام', 'ديباكين', 'ديسفينلافاكسين', 'دوكسيبين', 'دوغماتيل',
    'ديسولفيرام', 'دكسامفيتامين',
    # === ARABIC - ر ===
    'ريتالين', 'ريسبردال', 'ريسبيريدون', 'ريفوتريل', 'ريميرون', 'ريكسلتي',
    # === ARABIC - ز ===
    'زاناكس', 'زولبيديم', 'زولوفت', 'زيبراسيدون', 'زيبراكسا', 'زوبيكلون', 'زوكلوبنتيكسول',
    # === ARABIC - س ===
    'سبرالكس', 'ستراتيرا', 'ستلنكس', 'سيبرالكس', 'سيبراليكس', 'سيتالوبرام', 'سيرترالين',
    'سيروكسات', 'سيروكويل', 'سيليكسا', 'سيمبالتا', 'سولبيريد', 'سافريس',
    # === ARABIC - ف ===
    'فالبروات', 'فاليوم', 'فايفانس', 'فلوكسيتين', 'فينلافاكسين',
    'فلوفوكسامين', 'فافرين', 'فالدوكسان', 'فلوأنكسول', 'فلوبنتيكسول', 'فورتيوكسيتين',
    # === ARABIC - ك ===
    'كاربامازيبين', 'كلوربرومازين', 'كلوزابين', 'كلوزاريل', 'كلوميبرامين', 'كلونازيبام',
    'كونسيرتا', 'كويتيابين', 'كاريبرازين',
    # === ARABIC - ل ===
    'لاتودا', 'لاموتريجين', 'لاميكتال', 'لورازيبام', 'لوراسيدون', 'ليثيوم', 'ليريكا',
    'ليسديكسامفيتامين', 'ليكسوتانيل', 'ليبونيكس', 'لارجاكتيل', 'لوفوكس',
    # === ARABIC - م ===
    'ميثيلفينيديت', 'ميرتازابين', 'ميلاتونين', 'ميثادون',
    # === ARABIC - ن ===
    'نورتريبتيلين', 'نالتريكسون',
    # === ARABIC - هـ ===
    'هالوبيريدول', 'هالدول', 'هيدروكسيزين',
    # === ARABIC - و ===
    'ويلبوترين',
    # === ARABIC - Colloquial ===
    'حبوب السعادة', 'مهدئات', 'منومات', 'مضادات الاكتئاب', 'مضادات القلق',
    'مضادات الذهان', 'مثبتات المزاج', 'أدوية نفسية', 'ادوية نفسية',
    'حبوب نفسية', 'حبوب مهدئة', 'حبوب منومة', 'علاج نفسي دوائي',
    # === ENGLISH - Generic & Brand Names ===
    'abilfy', 'abilify', 'acamprosate', 'agomelatine', 'alprazolam', 'alprzolam',
    'amitriptilin', 'amitriptyline', 'anafranil', 'aripiprazole', 'asenapine',
    'ativan', 'atomoxetin', 'atomoxetine',
    'brexpiprazole', 'bromazepam', 'buprenorphine', 'bupropion', 'buproprion',
    'busparon', 'buspirone',
    'carbamazepine', 'carbamezapine', 'cariprazine', 'celexa', 'chlorpromazin',
    'chlorpromazine', 'cipralex', 'cipralix', 'citalopram', 'citaloprom',
    'clomipramin', 'clomipramine', 'clonazepam', 'clonazpam', 'clozapin',
    'clozapine', 'cymbalta',
    'depakine', 'desvenlafaxine', 'desvenlaflaxin', 'dexamfetamine', 'dexamphetamine',
    'diazapam', 'diazepam', 'disulfiram', 'dogmatil', 'doxepin',
    'duloxetin', 'duloxetine',
    'effexor', 'escitalopram', 'eszopiclone', 'eszopicolone', 'etizolam',
    'faverin', 'fluanxol', 'fluoxetin', 'fluoxetine', 'flupentixol', 'fluphenazine',
    'fluvoxamine',
    'gabapantine', 'gabapentin', 'guanfacine',
    'haldol', 'haloperidol', 'halopridol', 'hydroxizin', 'hydroxyzine',
    'imipramine', 'intuniv', 'invega',
    'lamictal', 'lamotregen', 'lamotrigine', 'largactil', 'latuda', 'leponex',
    'lexotanil', 'lis-dexamfetamine', 'lisdexamfetamine', 'lithium', 'lithyum',
    'lorazepam', 'lorazpam', 'lurasidon', 'lurasidone', 'luvox', 'lyrica',
    'melatonin', 'melatonine', 'methadone', 'methylphenidate', 'methyphenidate',
    'mirtazapin', 'mirtazapine', 'modafinil',
    'naltrexone', 'nortriptyline',
    'olanzapin', 'olanzapine', 'oxcarbazepine',
    'paliperidon', 'paliperidone', 'paroxetin', 'paroxetine', 'perphenazine',
    'prazocin', 'prazosin', 'pregabalin', 'pregablin', 'pristiq',
    'propanolol', 'propranolol', 'prozac',
    'quetiapine', 'quetipine',
    'remeron', 'rexulti', 'risperdal', 'risperidon', 'risperidone',
    'ritalin', 'rivotril',
    'saphris', 'sebralex', 'seroquel', 'seroxat', 'sertralin', 'sertraline',
    'stilnox', 'strattera', 'sulpiride',
    'tegretol', 'thioridazine', 'tofranil', 'topiramat', 'topiramate',
    'trazadon', 'trazodone', 'trileptal', 'trintellix',
    'valdoxan', 'valium', 'valporate', 'valproate',
    'venlafaxine', 'venlaflaxin', 'vortioxetine', 'vraylar', 'vyvanse',
    'wellbutrin',
    'xanax',
    'ziprasidon', 'ziprasidone', 'zoloft', 'zolpediem', 'zolpidem',
    'zopiclone', 'zuclopenthixol', 'zyprexa',
]


# ╔══════════════════════════════════════════════════════════════╗
# ║  PRE-COMPILED MEDICATION REGEX                              ║
# ╚══════════════════════════════════════════════════════════════╝

def _is_arabic(text: str) -> bool:
    return bool(text) and ('\u0600' <= text[0] <= '\u06FF' or
                           '\u0750' <= text[0] <= '\u077F' or
                           '\uFB50' <= text[0] <= '\uFDFF' or
                           '\uFE70' <= text[0] <= '\uFEFF')


def _build_medication_regex():
    arabic_meds, english_meds = [], []
    seen = set()
    for med in MEDICATION_KEYWORDS:
        med_lower = med.lower()
        if med_lower in seen:
            continue
        seen.add(med_lower)
        if _is_arabic(med):
            arabic_meds.append(re.escape(med_lower))
        else:
            english_meds.append(r'\b' + re.escape(med_lower) + r'\b')
    all_patterns = arabic_meds + english_meds
    all_patterns.sort(key=len, reverse=True)
    return re.compile('|'.join(all_patterns), re.IGNORECASE)


_MEDICATION_REGEX = _build_medication_regex()


def find_medications(text: str) -> List[str]:
    if not text:
        return []
    matches = _MEDICATION_REGEX.findall(text)
    seen = set()
    result = []
    for m in matches:
        m_lower = m.lower().strip()
        if m_lower not in seen:
            seen.add(m_lower)
            result.append(m)
    return result


# ╔══════════════════════════════════════════════════════════════╗
# ║  SEARCH PHRASE GENERATION (from Reddit v3.1)                ║
# ╚══════════════════════════════════════════════════════════════╝

def is_english_keyword(text: str) -> bool:
    return bool(re.match(r'^[a-zA-Z]', text))


def is_feminine_keyword(kw: str) -> bool:
    return kw in FEMININE_KEYWORDS


def phrase_needs_b_connector(phrase: str) -> bool:
    stripped = phrase.rstrip()
    return stripped.endswith(' ب') or stripped.endswith(' بـ') or stripped == 'ب'


def phrase_needs_min_connector(phrase: str) -> bool:
    stripped = phrase.rstrip()
    return stripped.endswith(' من') or stripped == 'من'


def generate_search_phrases(diagnosis_key: str) -> List[str]:
    config = DIAGNOSES[diagnosis_key]
    keywords = config.keywords
    keywords_restricted = config.keywords_restricted if config.keywords_restricted else []

    all_phrases = list(DIAGNOSIS_PHRASES)
    for culture_phrases in CULTURAL_PHRASES.values():
        all_phrases.extend(culture_phrases)
    all_phrases = list(set(all_phrases))

    # Categorize keywords
    base_keywords, al_keywords, compound_keywords = [], [], []
    for kw in keywords:
        if ' ' in kw:
            compound_keywords.append(kw)
        elif kw.startswith('ال'):
            al_keywords.append(kw)
        else:
            base_keywords.append(kw)

    base_restricted, al_restricted, compound_restricted = [], [], []
    for kw in keywords_restricted:
        if ' ' in kw:
            compound_restricted.append(kw)
        elif kw.startswith('ال'):
            al_restricted.append(kw)
        else:
            base_restricted.append(kw)

    phrases = set()

    # === CATEGORIZE PHRASES BY TYPE ===
    b_markers = [
        'اصبت', 'أصبت', 'مصاب', 'مصابة', 'مصابه',
        'مبتلي', 'مبتلية', 'مبتليه', 'ابتليت',
        'مريض', 'مريضة', 'مريضه',
        'شخصني', 'شخصوني', 'شخصتني', 'تم تشخيصي',
        'تشخصت', 'اتشخصت', 'شُخِّصت', 'شخصت',
        'إصابتي', 'اصابتي',
        'أكد التشخيص', 'اكد التشخيص',
        'أثبت التشخيص', 'اثبت التشخيص',
    ]
    b_phrases = [p for p in all_phrases if any(x in p for x in b_markers)]

    min_markers = ['اعاني', 'أعاني', 'بعاني', 'عم بعاني', 'تعالج', 'أتعالج', 'اتعالج']
    min_phrases = [p for p in all_phrases if any(x in p for x in min_markers)]

    direct_markers_masc = [
        'عندي', 'لدي', 'فيني', 'معي', 'معايا',
        'جاني', 'جالي', 'اجاني',
        'طلعلي', 'صار معي',
        'كاين', 'معايش', 'اعيش مع', 'أعيش مع', 'أتعايش مع', 'اتعايش مع',
        'تشخيصي', 'تشخيص', 'بواجه', 'بأواجه', 'اتضح', 'حصلت عليه',
    ]
    direct_markers_fem = [
        'جاتني', 'جاتلي', 'اجاتني',
        'طلعتلي', 'صارت معي',
        'معايشة', 'معايشه',
    ]
    diagnosis_markers = [
        'شخصني', 'شخصوني', 'شخصتني', 'تم تشخيصي',
        'تشخصت', 'اتشخصت', 'شُخِّصت', 'شخصت',
        'إصابتي', 'اصابتي',
        'أكد التشخيص', 'اكد التشخيص',
        'أثبت التشخيص', 'اثبت التشخيص',
    ]

    direct_phrases_masc = [p for p in all_phrases if any(x in p for x in direct_markers_masc)]
    direct_phrases_fem = [p for p in all_phrases if any(x in p for x in direct_markers_fem)]
    direct_phrases_masc = [p for p in direct_phrases_masc if not any(x in p for x in diagnosis_markers)]
    direct_phrases_fem = [p for p in direct_phrases_fem if not any(x in p for x in diagnosis_markers)]

    # === GENERATE WITH ب CONNECTOR ===
    for phrase in b_phrases:
        if phrase_needs_b_connector(phrase):
            continue
        for kw in al_keywords:
            phrases.add(f'"{phrase} بال{kw[2:]}"')
        for kw in base_keywords:
            if is_english_keyword(kw):
                phrases.add(f'"{phrase} ب{kw}"')
                phrases.add(f'"{phrase} ب {kw}"')
            else:
                phrases.add(f'"{phrase} ب{kw}"')
        for kw in compound_keywords:
            if is_english_keyword(kw):
                phrases.add(f'"{phrase} ب{kw}"')
                phrases.add(f'"{phrase} ب {kw}"')
            else:
                phrases.add(f'"{phrase} ب{kw}"')

    # === GENERATE WITH من CONNECTOR ===
    all_min_keywords = (al_keywords + base_keywords + compound_keywords +
                        al_restricted + base_restricted + compound_restricted)
    for phrase in min_phrases:
        if phrase_needs_min_connector(phrase):
            for kw in all_min_keywords:
                phrases.add(f'"{phrase} {kw}"')
        else:
            for kw in all_min_keywords:
                phrases.add(f'"{phrase} من {kw}"')

    # === GENERATE DIRECT COMBINATIONS ===
    for phrase in direct_phrases_masc:
        for kw in base_keywords + al_keywords + compound_keywords:
            phrases.add(f'"{phrase} {kw}"')
    for phrase in direct_phrases_fem:
        for kw in base_keywords + al_keywords + compound_keywords:
            if is_feminine_keyword(kw):
                phrases.add(f'"{phrase} {kw}"')

    # === COMMON TEMPLATES ===
    common_templates_b = [
        'انا مصاب ب{}', 'أنا مصاب ب{}',
        'انا مصابة ب{}', 'أنا مصابة ب{}',
        'انا مصابه ب{}', 'أنا مصابه ب{}',
        'كشخص مصاب ب{}',
        'تم تشخيصي ب{}', 'شخصوني ب{}', 'شخصني ب{}', 'شخصتني ب{}', 'شخصت ب{}',
        'انا مريض ب{}', 'أنا مريض ب{}',
        'انا مريضة ب{}', 'انا مريضه ب{}',
        'شخصني الطبيب ب{}', 'شخصني الدكتور ب{}',
        'شخصتني الطبيبة ب{}', 'شخصتني الطبيبه ب{}',
        'شخصتني الدكتورة ب{}', 'شخصتني الدكتوره ب{}',
        'الاخصائي شخصني ب{}', 'الأخصائي شخصني ب{}',
        'الأخصائية شخصتني ب{}', 'الأخصائيه شخصتني ب{}',
        'مبتلي ب{}', 'مبتلية ب{}', 'مبتليه ب{}',
        'ابتليت ب{}',
        'اصبت ب{}', 'أصبت ب{}',
        'طلعت مصاب ب{}', 'طلعت مصابة ب{}', 'طلعت مصابه ب{}',
        'لقيت نفسي مصاب ب{}', 'لقيت نفسي مصابة ب{}', 'لقيت نفسي مصابه ب{}',
        'اكتشفت إني مصاب ب{}', 'اكتشفت اني مصاب ب{}',
        'اكتشفت إني مصابة ب{}', 'اكتشفت اني مصابة ب{}',
        'عرفت إن أنا مصاب ب{}', 'عرفت ان أنا مصاب ب{}',
        'اتأكدت إني مصاب ب{}', 'اتأكدت اني مصاب ب{}',
        'اتأكدت إني مصابة ب{}', 'اتأكدت اني مصابة ب{}',
        'أكد الطبيب إصابتي ب{}', 'أكد الدكتور إصابتي ب{}',
        'الدكتور أكد إصابتي ب{}', 'الطبيب أكد إصابتي ب{}',
        'تم التأكيد على إصابتي ب{}', 'تم إثبات إصابتي ب{}',
        'الدكتور أكد التشخيص ب{}', 'الطبيب أكد التشخيص ب{}',
        'الدكتور أثبت التشخيص ب{}', 'الطبيب أثبت التشخيص ب{}',
        'كنت مصاب ب{}', 'كنت مصابة ب{}', 'كنت مصابه ب{}',
    ]

    common_templates_min = [
        'اعاني من {}', 'أعاني من {}', 'بعاني من {}',
    ]

    common_templates_direct = [
        'عندي {}', 'أنا عندي {}', 'انا عندي {}',
        'لدي {}', 'فيني {}',
        'تشخيصي هو {}', 'طلع تشخيصي {}',
        'طلعت عندي {}', 'طلع عندي {}',
        'لقيت نفسي عندي {}',
        'عرفت إني عندي {}', 'عرفت اني عندي {}',
        'اكتشفت إن عندي {}', 'اكتشفت ان عندي {}',
        'اتأكدت إن عندي {}', 'اتأكدت ان عندي {}',
        'بعد التشخيص طلع عندي {}',
        'تشخيص الطبيب هو {}', 'تشخيص الدكتور هو {}',
        'تشخيص الطبيب كان {}', 'تشخيص الدكتور كان {}',
        'تشخيص حالتي هو {}', 'تشخيص حالتي كان {}',
        'طلع إن التشخيص هو {}', 'طلع ان التشخيص هو {}',
        'اتضح إن التشخيص كان {}', 'اتضح ان التشخيص كان {}',
        'أنا بواجه مشكلة اسمها {}', 'انا بواجه مشكلة اسمها {}',
    ]

    main_keywords = keywords[:4]

    for template in common_templates_b:
        for kw in main_keywords:
            if 'ب{}' in template:
                if kw.startswith('ال'):
                    search = template.replace(' ب{}', ' بال' + kw[2:])
                    phrases.add(f'"{search}"')
                elif is_english_keyword(kw):
                    phrases.add(f'"{template.format(kw)}"')
                    phrases.add(f'"{template.replace("ب{}", "ب " + kw)}"')
                else:
                    phrases.add(f'"{template.format(kw)}"')

    main_all = main_keywords + keywords_restricted[:2] if keywords_restricted else main_keywords
    for template in common_templates_min:
        for kw in main_all:
            phrases.add(f'"{template.format(kw)}"')

    for template in common_templates_direct:
        for kw in main_keywords:
            phrases.add(f'"{template.format(kw)}"')

    # === GRAMMAR VALIDATION ===
    cleaned = set()
    for p in phrases:
        p = re.sub(r'\s+', ' ', p)
        skip = False
        if re.search(r' ب ب', p): skip = True
        if 'بب' in p and 'ببوردرلاين' not in p: skip = True
        if 'من من' in p: skip = True
        if 'منال' in p or 'مناضطراب' in p: skip = True
        if 'مصابال' in p or 'مصابةال' in p or 'مصابهال' in p: skip = True
        if 'اضطراب اضطراب' in p: skip = True
        if 'قالي ب' in p: skip = True
        if 'انكشفت ب' in p: skip = True
        if 'بعلى ' in p or 'بعلي ' in p: skip = True
        if 'من على ' in p or 'من علي ' in p: skip = True
        if 'مع على ' in p or 'مع علي ' in p: skip = True
        if 'بأنا ' in p: skip = True
        if not skip:
            cleaned.add(p)

    return sorted(list(cleaned))


# ╔══════════════════════════════════════════════════════════════╗
# ║  ARABIC WORD-BOUNDARY CHECKS                               ║
# ╚══════════════════════════════════════════════════════════════╝

def _is_arabic_char(ch: str) -> bool:
    return ('\u0600' <= ch <= '\u06FF' or
            '\u0750' <= ch <= '\u077F' or
            '\uFB50' <= ch <= '\uFDFF' or
            '\uFE70' <= ch <= '\uFEFF')


ARABIC_BOUNDARY_PHRASES = {
    'معي', 'لدي', 'فيني', 'جاني', 'جالي', 'عندي',
}
ARABIC_BOUNDARY_PHRASES.discard('شخصت')


def _is_arabic_boundary(text: str, term: str, match_start: int, match_end: int) -> bool:
    if term not in ARABIC_BOUNDARY_PHRASES:
        return True
    if match_start > 0:
        if _is_arabic_char(text[match_start - 1]):
            return False
    if match_end < len(text):
        if _is_arabic_char(text[match_end]):
            return False
    return True


def _find_all_occurrences(text_lower: str, term: str) -> List[Tuple[int, int]]:
    term_lower = term.strip('"').lower()
    positions = []
    if is_english_keyword(term_lower):
        pattern = re.compile(r'\b' + re.escape(term_lower) + r'\b')
        for m in pattern.finditer(text_lower):
            positions.append((m.start(), m.end()))
    else:
        start = 0
        while True:
            pos = text_lower.find(term_lower, start)
            if pos == -1:
                break
            match_end = pos + len(term_lower)
            if _is_arabic_boundary(text_lower, term_lower, pos, match_end):
                positions.append((pos, match_end))
            start = pos + 1
    return positions


# ╔══════════════════════════════════════════════════════════════╗
# ║  GRAMMAR-AWARE CATEGORIZED PHRASES (Stage 2)               ║
# ╚══════════════════════════════════════════════════════════════╝

@dataclass
class CategorizedPhrase:
    phrase: str
    connector_type: str  # 'b', 'min', 'min_needs', 'direct', 'direct_fem'


def _build_categorized_disclosure_phrases() -> List[CategorizedPhrase]:
    all_phrases = list(DIAGNOSIS_PHRASES)
    for culture_phrases in CULTURAL_PHRASES.values():
        all_phrases.extend(culture_phrases)
    all_phrases = list(set(all_phrases))

    b_markers = [
        'اصبت', 'أصبت', 'مصاب', 'مصابة', 'مصابه',
        'مبتلي', 'مبتلية', 'مبتليه', 'ابتليت',
        'مريض', 'مريضة', 'مريضه',
        'شخصني', 'شخصوني', 'شخصتني', 'تم تشخيصي',
        'تشخصت', 'اتشخصت', 'شُخِّصت', 'شخصت',
        'إصابتي', 'اصابتي',
        'أكد التشخيص', 'اكد التشخيص',
        'أثبت التشخيص', 'اثبت التشخيص',
    ]
    min_markers = ['اعاني', 'أعاني', 'بعاني', 'عم بعاني', 'تعالج', 'أتعالج', 'اتعالج']
    direct_markers_masc = [
        'عندي', 'لدي', 'فيني', 'معي', 'معايا',
        'جاني', 'جالي', 'اجاني',
        'طلعلي', 'صار معي',
        'كاين', 'معايش', 'اعيش مع', 'أعيش مع', 'أتعايش مع', 'اتعايش مع',
        'تشخيصي', 'تشخيص', 'بواجه', 'بأواجه', 'اتضح', 'حصلت عليه',
    ]
    direct_markers_fem = [
        'جاتني', 'جاتلي', 'اجاتني', 'طلعتلي', 'صارت معي', 'معايشة', 'معايشه',
    ]
    diagnosis_markers = [
        'شخصني', 'شخصوني', 'شخصتني', 'تم تشخيصي',
        'تشخصت', 'اتشخصت', 'شُخِّصت', 'شخصت',
        'إصابتي', 'اصابتي',
        'أكد التشخيص', 'اكد التشخيص',
        'أثبت التشخيص', 'اثبت التشخيص',
    ]

    categorized = []
    for phrase in all_phrases:
        is_b = any(x in phrase for x in b_markers)
        is_min = any(x in phrase for x in min_markers)
        is_direct_masc = any(x in phrase for x in direct_markers_masc)
        is_direct_fem = any(x in phrase for x in direct_markers_fem)
        is_diagnosis = any(x in phrase for x in diagnosis_markers)

        if is_b:
            categorized.append(CategorizedPhrase(phrase=phrase, connector_type='b'))
        elif is_min:
            if phrase_needs_min_connector(phrase):
                categorized.append(CategorizedPhrase(phrase=phrase, connector_type='min'))
            else:
                categorized.append(CategorizedPhrase(phrase=phrase, connector_type='min_needs'))
        elif is_direct_fem and not is_diagnosis:
            categorized.append(CategorizedPhrase(phrase=phrase, connector_type='direct_fem'))
        elif is_direct_masc and not is_diagnosis:
            categorized.append(CategorizedPhrase(phrase=phrase, connector_type='direct'))

    return categorized


_CATEGORIZED_DISCLOSURE_PHRASES = _build_categorized_disclosure_phrases()


# ╔══════════════════════════════════════════════════════════════╗
# ║  CONNECTOR-AWARE KEYWORD FORMS (Stage 2)                   ║
# ╚══════════════════════════════════════════════════════════════╝

@lru_cache(maxsize=32)
def _build_keyword_forms_for_condition(condition: str) -> Dict[str, List[Tuple[str, str]]]:
    config = DIAGNOSES[condition]
    regular_keywords = config.keywords
    restricted_keywords = config.keywords_restricted if config.keywords_restricted else []

    base_keywords, al_keywords, compound_keywords = [], [], []
    for kw in regular_keywords:
        if ' ' in kw: compound_keywords.append(kw)
        elif kw.startswith('ال'): al_keywords.append(kw)
        else: base_keywords.append(kw)

    base_restricted, al_restricted, compound_restricted = [], [], []
    for kw in restricted_keywords:
        if ' ' in kw: compound_restricted.append(kw)
        elif kw.startswith('ال'): al_restricted.append(kw)
        else: base_restricted.append(kw)

    fem_keywords = {kw for kw in regular_keywords if is_feminine_keyword(kw)}
    regular_kw_list = al_keywords + base_keywords + compound_keywords
    restricted_kw_list = al_restricted + base_restricted + compound_restricted
    all_kw_list_for_min = regular_kw_list + restricted_kw_list

    seen = {ct: set() for ct in ['b', 'min', 'min_needs', 'direct', 'direct_fem']}
    forms = {ct: [] for ct in seen}

    # ب connector forms
    for kw in al_keywords:
        kw_lower = kw.lower()
        for form in [f'بال{kw_lower[2:]}', f'ب {kw_lower}']:
            if form not in seen['b']:
                seen['b'].add(form); forms['b'].append((form, kw))
    for kw in base_keywords + compound_keywords:
        kw_lower = kw.lower()
        for form in [f'ب{kw_lower}', f'ب {kw_lower}']:
            if form not in seen['b']:
                seen['b'].add(form); forms['b'].append((form, kw))

    # من connector forms
    for kw in all_kw_list_for_min:
        kw_lower = kw.lower()
        if kw_lower not in seen['min']:
            seen['min'].add(kw_lower); forms['min'].append((kw_lower, kw))
        form = f'من {kw_lower}'
        if form not in seen['min_needs']:
            seen['min_needs'].add(form); forms['min_needs'].append((form, kw))

    # Direct forms
    for kw in regular_kw_list:
        kw_lower = kw.lower()
        if kw_lower not in seen['direct']:
            seen['direct'].add(kw_lower); forms['direct'].append((kw_lower, kw))
        if kw in fem_keywords and kw_lower not in seen['direct_fem']:
            seen['direct_fem'].add(kw_lower); forms['direct_fem'].append((kw_lower, kw))

    for ct in forms:
        forms[ct].sort(key=lambda x: len(x[0]), reverse=True)
    return forms


def _find_keyword_form_in_window(
    window_text: str, text_lower: str, p_end: int,
    search_form: str, is_connector_fused: bool
) -> Optional[int]:
    if is_english_keyword(search_form.lstrip('ب ').lstrip()):
        if is_connector_fused:
            pattern = re.compile(re.escape(search_form) + r'\b')
        else:
            pattern = re.compile(r'\b' + re.escape(search_form) + r'\b')
        m = pattern.search(window_text)
        return m.start() if m else None
    else:
        search_start = 0
        while True:
            pos = window_text.find(search_form, search_start)
            if pos == -1:
                return None
            abs_pos = p_end + pos
            abs_end = abs_pos + len(search_form)
            left_ok = (abs_pos == 0 or not _is_arabic_char(text_lower[abs_pos - 1]))
            right_ok = (abs_end >= len(text_lower) or not _is_arabic_char(text_lower[abs_end]))
            if left_ok and right_ok:
                return pos
            search_start = pos + 1


def match_text(
    text: str, condition: str,
    max_distance: int = PROXIMITY_DISTANCE,
) -> Tuple[bool, str, str, int, int]:
    """Grammar-aware anchored proximity matching (Stage 2)."""
    if not text:
        return False, '', '', -1, -1

    text_lower = text.lower()
    keyword_forms = _build_keyword_forms_for_condition(condition)

    for cp in _CATEGORIZED_DISCLOSURE_PHRASES:
        phrase_lower = cp.phrase.lower()
        for p_start, p_end in _find_all_occurrences(text_lower, phrase_lower):
            window_end = min(len(text_lower), p_end + max_distance)
            window_text = text_lower[p_end:window_end]
            appropriate_forms = keyword_forms.get(cp.connector_type, [])
            is_fused = cp.connector_type == 'b'

            for search_form, original_kw in appropriate_forms:
                pos = _find_keyword_form_in_window(
                    window_text=window_text, text_lower=text_lower,
                    p_end=p_end, search_form=search_form,
                    is_connector_fused=is_fused,
                )
                if pos is not None:
                    return True, cp.phrase, original_kw, pos, p_start

    return False, '', '', -1, -1




# ============================================================
# TWEET COLLECTION (v3-3 timing + v4 features)
# ============================================================

async def collect_tweets(
    diagnosis_key: str,
    cookies_file: str = 'cookies.json',
    output_prefix: str = None,
    max_batches_per_phrase: int = 10,
    max_phrases: int = None,
    output_dir: str = None,
) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
    """Collect tweets matching diagnosis self-disclosure patterns."""
    if diagnosis_key not in DIAGNOSES:
        print(f"❌ Unknown diagnosis: {diagnosis_key}")
        print(f"   Available: {', '.join(DIAGNOSES.keys())}")
        return None, None

    config = DIAGNOSES[diagnosis_key]

    print(f'\n{"="*70}')
    print(f'ARABIC MENTAL HEALTH COLLECTOR v4')
    print(f'{"="*70}')
    print(f'Diagnosis: {config.name_ar} ({config.name})')
    print(f'Keywords: {len(config.keywords)}')
    if config.keywords_restricted:
        print(f'Restricted Keywords: {len(config.keywords_restricted)}')
    print(f'Proximity Distance: {PROXIMITY_DISTANCE} characters')

    search_phrases = generate_search_phrases(diagnosis_key)
    if max_phrases:
        search_phrases = search_phrases[:max_phrases]

    print(f'Search Phrases: {len(search_phrases)}')
    print(f'{"="*70}\n')

    # === v3-3 LOGIN (preserved exactly) ===
    client = Client(language='ar')

    if not os.path.exists(cookies_file):
        print(f'❌ Cookies file not found: {cookies_file}')
        return None, None

    client.load_cookies(cookies_file)
    print('✅ Loaded Twitter cookies')

    all_tweets = []
    seen_ids = set()

    # v4: tracking stats
    stats = {'searched': 0, 'fetched': 0, 'matched': 0, 'skipped_rt': 0}
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 5
    collection_start_time = time.time()

    # v4.5: progress saving (interval raised to 50 to reduce Drive I/O)
    PROGRESS_SAVE_INTERVAL = 50
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    prefix = output_prefix or f'arabic_{diagnosis_key}'
    # v4.5: Use output_dir (defaults to OUTPUT_FOLDER)
    save_dir = output_dir or OUTPUT_FOLDER
    os.makedirs(save_dir, exist_ok=True)
    progress_file = os.path.join(save_dir, f'{prefix}_progress_{timestamp}.csv')

    for i, phrase in enumerate(search_phrases, 1):
        display_q = phrase.strip('"')
        if len(display_q) > 70:
            display_q = display_q[:67] + '...'
        print(f'\n[{i}/{len(search_phrases)}] Searching: {display_q}')

        try:
            query = phrase.strip('"')

            # === v3-3 RATE LIMIT HANDLING (preserved exactly) ===
            try:
                tweets = await client.search_tweet(query, product='Latest')
            except TooManyRequests:
                print(f'   ⏳ Rate limit! Waiting 15 minutes...')
                await asyncio.sleep(900)
                tweets = await client.search_tweet(query, product='Latest')

            batch_count = 0
            empty_count = 0

            # === v3-3 BATCH LOOP (preserved exactly: max_batches_per_phrase default=10) ===
            while tweets and batch_count < max_batches_per_phrase:
                new_count = 0
                match_count = 0

                for tweet in tweets:
                    if tweet.id in seen_ids:
                        continue
                    seen_ids.add(tweet.id)

                    # v4: Skip retweets (keep originals + replies only)
                    tweet_text = getattr(tweet, 'text', '') or ''
                    if tweet_text.startswith('RT @'):
                        stats['skipped_rt'] += 1
                        continue
                    if getattr(tweet, 'is_retweet', False):
                        stats['skipped_rt'] += 1
                        continue
                    if getattr(tweet, 'retweeted_tweet', None) is not None:
                        stats['skipped_rt'] += 1
                        continue

                    new_count += 1
                    stats['fetched'] += 1

                    # === FORWARD-ONLY 40-CHAR GRAMMAR-AWARE MATCHING ===
                    is_match, matched_phrase, matched_keyword, distance, phrase_start = match_text(
                        tweet.text, diagnosis_key, PROXIMITY_DISTANCE
                    )

                    if is_match:
                        # v4: medication detection
                        medications = find_medications(tweet.text)

                        tweet_data = {
                            'tweet_id': tweet.id,
                            'text': tweet.text,
                            'user_id': getattr(tweet.user, 'id', '') if tweet.user else '',
                            'username': getattr(tweet.user, 'screen_name', '') if tweet.user else '',
                            'user_name': getattr(tweet.user, 'name', '') if tweet.user else '',
                            'user_bio': getattr(tweet.user, 'description', '') if tweet.user else '',
                            'followers_count': getattr(tweet.user, 'followers_count', 0) if tweet.user else 0,
                            # v4: extra metadata
                            'user_location': getattr(tweet.user, 'location', '') if tweet.user else '',
                            'statuses_count': getattr(tweet.user, 'statuses_count', 0) if tweet.user else 0,
                            'profile_url': f"https://twitter.com/{getattr(tweet.user, 'screen_name', '')}" if tweet.user and getattr(tweet.user, 'screen_name', '') else '',
                            'created_at': str(tweet.created_at) if hasattr(tweet, 'created_at') and tweet.created_at else '',
                            'retweet_count': getattr(tweet, 'retweet_count', 0),
                            'favorite_count': getattr(tweet, 'favorite_count', 0),
                            'reply_count': getattr(tweet, 'reply_count', 0),
                            'is_reply': getattr(tweet, 'in_reply_to_tweet_id', None) is not None or getattr(tweet, 'reply_to', None) is not None,
                            'tweet_url': f"https://twitter.com/{getattr(tweet.user, 'screen_name', '')}/status/{tweet.id}" if tweet.user else '',
                            'search_phrase': phrase,
                            'matched_phrase': matched_phrase,
                            'matched_keyword': matched_keyword,
                            # forward-only 40-char distance
                            'match_distance': distance,
                            'diagnosis': diagnosis_key,
                            # v4: medication detection
                            'medications_found': ', '.join(medications) if medications else '',
                        }
                        all_tweets.append(tweet_data)
                        match_count += 1
                        stats['matched'] += 1
                        print(f'   ✓ Match found (distance={distance})')

                print(f'   Batch {batch_count + 1}: fetched={new_count}, matched={match_count}')

                # === v4.5 EMPTY BATCH TRACKING (reduced from 3 to 2) ===
                if new_count == 0:
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0

                batch_count += 1

                # === v4.5 PAGINATION DELAY (reduced from 3-6s) ===
                try:
                    await asyncio.sleep(randint(2, 4))
                    tweets = await tweets.next()
                except TooManyRequests:
                    print(f'   ⏳ Rate limit on pagination! Waiting 15 minutes...')
                    await asyncio.sleep(900)
                    try:
                        tweets = await tweets.next()
                    except Exception:
                        break
                except Exception:
                    break

        # === v4: CONSECUTIVE ERROR TRACKING ===
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'Rate limit' in error_msg.lower():
                print(f'   ⏳ Rate limit! Waiting 15 minutes...')
                await asyncio.sleep(900)
                consecutive_errors = 0
            elif '404' in error_msg:
                consecutive_errors += 1
                print(f'   ❌ Error 404 (consecutive: {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS})')
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f'\n{"="*70}')
                    print(f'⚠️  ABORTING: {MAX_CONSECUTIVE_ERRORS} consecutive 404 errors.')
                    print(f'   Your Twitter cookies have likely expired.')
                    print(f'   To fix: re-login via twikit and save new cookies.json')
                    print(f'{"="*70}')
                    break
            else:
                consecutive_errors += 1
                print(f'   ❌ Error: {e}')
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f'\n⚠️  ABORTING: {MAX_CONSECUTIVE_ERRORS} consecutive errors.')
                    break
            continue

        # Reset consecutive errors on success
        consecutive_errors = 0
        stats['searched'] += 1

        # v4: Progress save
        if all_tweets and stats['searched'] % PROGRESS_SAVE_INTERVAL == 0:
            progress_df = pd.DataFrame(all_tweets)
            progress_df.to_csv(progress_file, index=False, encoding='utf-8-sig')
            print(f'\n   💾 Progress saved: {len(all_tweets)} matches → {progress_file}')

        # v4: ETA estimate
        if stats['searched'] >= 3:
            elapsed = time.time() - collection_start_time
            rate = elapsed / stats['searched']
            remaining = (len(search_phrases) - i) * rate
            if remaining > 3600:
                eta_str = f'{remaining/3600:.1f} hours'
            elif remaining > 60:
                eta_str = f'{remaining/60:.1f} min'
            else:
                eta_str = f'{remaining:.0f}s'
            if i % 20 == 0:
                print(f'   📊 Progress: {i}/{len(search_phrases)} | {stats["matched"]} matches | ETA: {eta_str}')

        # === v4.5 PHRASE DELAY (reduced from 8-12s) ===
        await asyncio.sleep(randint(4, 7))

    # === SAVE RESULTS AS CSV ===
    if all_tweets:
        df = pd.DataFrame(all_tweets)

        filename = os.path.join(save_dir, f'{prefix}_{timestamp}.csv')
        summary_file = os.path.join(save_dir, f'{prefix}_summary_{timestamp}.csv')
        kwdist_file = os.path.join(save_dir, f'{prefix}_keyword_dist_{timestamp}.csv')

        # Main results
        df.to_csv(filename, index=False, encoding='utf-8-sig')

        # Summary
        summary = pd.DataFrame({
            'Metric': [
                'Diagnosis', 'Total Tweets', 'Unique Users',
                'Search Phrases Used', 'Proximity Distance',
                'Collection Date', 'Tweets with Medications',
                'Tweets Fetched (before NLP)', 'Retweets Skipped',
            ],
            'Value': [
                f'{config.name_ar} ({config.name})',
                len(all_tweets),
                df['user_id'].nunique(),
                len(search_phrases),
                PROXIMITY_DISTANCE,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                (df['medications_found'] != '').sum(),
                stats['fetched'],
                stats['skipped_rt'],
            ]
        })
        summary.to_csv(summary_file, index=False, encoding='utf-8-sig')

        # Keyword distribution
        kw_dist = df['matched_keyword'].value_counts().reset_index()
        kw_dist.columns = ['Keyword', 'Count']
        kw_dist.to_csv(kwdist_file, index=False, encoding='utf-8-sig')

        print(f'\n{"="*70}')
        print(f'COLLECTION COMPLETE!')
        print(f'{"="*70}')
        print(f'Diagnosis: {config.name_ar} ({config.name})')
        print(f'Total Tweets: {len(all_tweets)}')
        print(f'Unique Users: {df["user_id"].nunique()}')
        med_count = (df['medications_found'] != '').sum()
        print(f'Tweets with Medications: {med_count}')
        print(f'File: {filename}')
        print(f'{"="*70}')

        # Clean up progress file
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
            except OSError:
                pass

        return filename, df
    else:
        print('\n❌ No tweets found.')
        return None, None


# ============================================================
# STANDALONE RUNNER — delusional_disorder (#2/21)
# Cookies: cookies_2.json
# Output:  /content/drive/MyDrive/Twitter_Mental_Health-delusional_disorder
# ============================================================

CONDITION = "delusional_disorder"
COOKIES_FILE = "cookies_2.json"

async def run():
    """Run collection for delusional_disorder only."""
    print(f"\n{'='*70}")
    print(f"STANDALONE MODE — delusional_disorder (#2/21)")
    print(f"Cookies: cookies_2.json")
    print(f"Output:  {OUTPUT_FOLDER}")
    print(f"{'='*70}\n")

    filename, df = await collect_tweets(
        diagnosis_key=CONDITION,
        cookies_file=COOKIES_FILE,
        max_batches_per_phrase=10,
        output_dir=OUTPUT_FOLDER,
    )

    if df is not None and len(df) > 0:
        print(f"\n✅ DONE — {len(df):,} tweets collected for delusional_disorder")
        print(f"   File: {filename}")
    else:
        print(f"\n⚠️  No tweets found for delusional_disorder")


if __name__ == "__main__":
    asyncio.run(run())
