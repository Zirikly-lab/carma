import os
import re
import sys
import time
import pandas as pd
import fasttext
import warnings
from collections import Counter
from datetime import datetime
from google.colab import drive
drive.mount('/content/drive')
import pandas as pd

# Suppress all warnings
warnings.filterwarnings('ignore')

# Suppress FastText logging
fasttext.FastText.eprint = lambda x: None

# ===============================
# Setup Logging with Emojis for better visibility
# ===============================
class Logger:
    def __init__(self):
        self.start_time = time.time()
        self.last_progress = 0

    def print_header(self, text):
        print("\n" + "="*70)
        print(f"🔷 {text}")
        print("="*70)
        sys.stdout.flush()

    def print_success(self, text):
        print(f"✅ {text}")
        sys.stdout.flush()

    def print_info(self, text):
        print(f"📌 {text}")
        sys.stdout.flush()

    def print_warning(self, text):
        print(f"⚠️ {text}")
        sys.stdout.flush()

    def print_error(self, text):
        print(f"❌ {text}")
        sys.stdout.flush()

    def print_progress(self, current, total, extra_info=""):
        percentage = (current / total) * 100
        # Update every 1% or every 100 posts (whichever is more frequent)
        if percentage - self.last_progress >= 1 or current % 100 == 0:
            bar_length = 40
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            elapsed = time.time() - self.start_time
            posts_per_sec = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / posts_per_sec if posts_per_sec > 0 else 0

            print(f"\r🔄 Progress: |{bar}| {current}/{total} ({percentage:.1f}%) | Speed: {posts_per_sec:.1f} posts/s | ETA: {eta:.1f}s {extra_info}", end='')
            sys.stdout.flush()
            self.last_progress = percentage

    def print_final(self):
        elapsed = time.time() - self.start_time
        print(f"\n⏱️  Total execution time: {elapsed:.2f} seconds")
        sys.stdout.flush()

logger = Logger()

# ===============================
# Download FastText language model if not exists
# ===============================
logger.print_header("INITIALIZING LANGUAGE DETECTION MODEL")

try:
    if not os.path.exists('lid.176.bin'):
        logger.print_info("Downloading FastText language model...")
        import subprocess
        result = subprocess.run(['wget', '-q', 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.print_error("Failed to download model. Trying with urllib...")
            import urllib.request
            urllib.request.urlretrieve('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'lid.176.bin')
        logger.print_success("Model downloaded successfully")
    else:
        logger.print_success("Model already exists locally")

    ft_model = fasttext.load_model('lid.176.bin')
    logger.print_success("FastText model loaded successfully")

except Exception as e:
    logger.print_error(f"Error loading FastText model: {str(e)}")
    logger.print_warning("Continuing with Arabic ratio detection only")
    ft_model = None

# ===============================
# Load and prepare data
# ===============================
logger.print_header("LOADING DATA")

try:
    # Make a safe copy
    df = df_all_posts.copy() if 'df_all_posts' in globals() or 'df_all_posts' in locals() else None

    if df is None:
        logger.print_error("df_all_posts not found. Please ensure it exists.")
        sys.exit(1)

    total_rows = len(df)
    logger.print_success(f"Loaded {total_rows:,} posts from dataset")

    # Validate required columns
    required_cols = ['selftext', 'id', 'title', 'subreddit', 'score', 'over_18', 'created_utc']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.print_warning(f"Missing columns: {missing_cols}. Will use available columns only.")

except Exception as e:
    logger.print_error(f"Error loading data: {str(e)}")
    sys.exit(1)

# ===============================
# Mental Health Keywords
# ===============================
CONDITION_KEYWORDS = ['فصام', 'الفصام', 'شيزوفرينيا', 'الشيزوفرينيا', 'اضطراب الفصام', 'انفصام الشخصية', 'انفصام الشخصيه', 'فصام الشخصية', 'فصام الشخصيه', 'أنفصام الشخصية', 'اضطراب ذهاني', 'psychotic disorder', 'schizophrenia', 'الاضطراب الفصامي الوجداني', 'الاضطراب الفصامي العاطفي', 'فصام وجداني', 'فصام عاطفي', 'اضطراب فصامي وجداني', 'سكيزوأفكتيف', 'سكيزو افيكتيف', 'schizoaffective disorder', 'schizoaffective', 'الاضطراب الوهمي', 'اضطراب وهمي', 'الاضطراب الضلالي', 'اضطراب ضلالي', 'الاضطراب الوهامي', 'اضطراب الأوهام', 'اضطراب الاوهام', 'أوهام مرضية', 'delusional disorder', 'delusional disorder NOS', 'ثنائي القطب', 'اضطراب ثنائي القطب', 'bipolar', 'bipolar disorder', 'بايبولار', 'بايبولر', 'manic-depressive illness', 'ثنائي القطب النوع الأول', 'ثنائي القطب النوع الاول', 'ثنائي القطب النوع الثاني', 'bipolar I', 'bipolar II', 'bipolar 1', 'bipolar 2', 'بايبولار 1', 'بايبولار 2', 'هوس خفيف', 'الهوس الخفيف', 'نوبة هوسية', 'نوبات هوسية', 'نوبة مانيا', 'نوبات مانيا', 'مانيا', 'hypomania', 'mania', 'manic episode', 'سيكلوثيميا', 'سيكلوثيمية', 'الاضطراب الدوري', 'اضطراب دوري', 'cyclothymia', 'cyclothymic disorder', 'اكتئاب', 'الاكتئاب', 'الإكتئاب', 'إكتئاب', 'depression', 'ديبريشن', 'دبرشن', 'ديبرشن', 'الاضطراب الاكتئابي الجسيم', 'اضطراب اكتئابي جسيم', 'نوبة اكتئاب جسيم', 'نوبة الاكتئاب الجسيم', 'اكتئاب حاد', 'اكتئاب شديد', 'اكتئاب مزمن', 'اكتئاب متوسط', 'الاضطراب الاكتئابي', 'اضطراب اكتئابي', 'الاكتئاب السريري', 'اكتئاب سريري', 'الاكتئاب الحاد', 'الاكتئاب الشديد', 'اضطراب الاكتئاب الرئيسي', 'الاكتئاب الرئيسي', 'أكتئاب', 'أكتئاب حاد', 'أكتئاب شديد', 'أكتئاب متوسط', 'أكتئاب مزمن', 'أكتئاب سريري', 'اكتأب', 'اكتاب', 'major depressive disorder', 'clinical depression', 'depressive disorder', 'MDD']
FEMININE_KEYWORDS = ['نوبة هلع', 'نوبه هلع', 'نوبة ذعر', 'نوبه ذعر', 'نوبات هلع', 'نوبات الذعر', 'صدمة نفسية', 'صدمه نفسيه', 'صدمات نفسية', 'صدمات نفسيه', 'الشخصية الحدية', 'الشخصيه الحديه', 'الشخصية النرجسية', 'الشخصيه النرجسيه', 'الشخصية الانعزالية', 'الشخصيه الانعزاليه', 'الشخصية الانطوائية', 'الشخصيه الانطوائيه', 'افكار انتحارية', 'أفكار انتحارية', 'افكار انتحاريه', 'أفكار انتحاريه', 'افكار وسواسية', 'أفكار وسواسية', 'افكار وسواسيه', 'أفكار وسواسيه', 'الأفعال القهرية', 'الأفعال القهريه', 'الافعال القهرية', 'الافعال القهريه', 'الشيزوفرينيا', 'شيزوفرينيا', 'انفصام الشخصية', 'انفصام الشخصيه', 'فقدان الشهية', 'فقدان الشهيه', 'فقدان الشهية العصبي', 'فقدان الشهيه العصبي', 'هوية تفارقية', 'هويه تفارقيه']
MEDICATION_KEYWORDS = ['أبيليفاي', 'أتوموكسيتين', 'أتيفان', 'أريبيبرازول', 'ألبرازولام', 'أميتريبتيلين', 'أنافرانيل', 'أولانزابين', 'أوكسكاربازيبين', 'أسينابين', 'أغوميلاتين', 'أكامبروسيت', 'إسيتالوبرام', 'إفكسور', 'إنفيغا', 'إيزوبيكلون', 'إيميبرامين', 'ابيليفاي', 'اتوموكسيتين', 'اتيفان', 'اريبيبرازول', 'افكسور', 'اميتريبتيلين', 'انافرانيل', 'انفيغا', 'اولانزابين', 'ايزوبيكلون', 'ايميبرامين', 'اسينابين', 'اغوميلاتين', 'اوكسكاربازيبين', 'اكامبروسيت', 'باروكستين', 'باروكسيتين', 'باليبيريدون', 'برازوسين', 'بروبرانولول', 'بروزاك', 'بريجابالين', 'بريستيك', 'بوبروبيون', 'بوسبيرون', 'برومازيبام', 'بريكسبيبرازول', 'بوبرينورفين', 'بيرفينازين', 'ترازودون', 'تربتيزول', 'توبيراميت', 'تيجريتول', 'توفرانيل', 'تريلبتال', 'ترينتليكس', 'جابابنتين', 'دولوكستين', 'ديازيبام', 'ديباكين', 'ديسفينلافاكسين', 'دوكسيبين', 'دوغماتيل', 'ديسولفيرام', 'دكسامفيتامين', 'ريتالين', 'ريسبردال', 'ريسبيريدون', 'ريفوتريل', 'ريميرون', 'ريكسلتي', 'زاناكس', 'زولبيديم', 'زولوفت', 'زيبراسيدون', 'زيبراكسا', 'زوبيكلون', 'زوكلوبنتيكسول', 'سبرالكس', 'ستراتيرا', 'ستلنكس', 'سيبرالكس', 'سيبراليكس', 'سيتالوبرام', 'سيرترالين', 'سيروكسات', 'سيروكويل', 'سيليكسا', 'سيمبالتا', 'سولبيريد', 'سافريس', 'فالبروات', 'فاليوم', 'فايفانس', 'فلوكسيتين', 'فينلافاكسين', 'فلوفوكسامين', 'فافرين', 'فالدوكسان', 'فلوأنكسول', 'فلوبنتيكسول', 'فورتيوكسيتين', 'كاربامازيبين', 'كلوربرومازين', 'كلوزابين', 'كلوزاريل', 'كلوميبرامين', 'كلونازيبام', 'كونسيرتا', 'كويتيابين', 'كاريبرازين', 'لاتودا', 'لاموتريجين', 'لاميكتال', 'لورازيبام', 'لوراسيدون', 'ليثيوم', 'ليريكا', 'ليسديكسامفيتامين', 'ليكسوتانيل', 'ليبونيكس', 'لارجاكتيل', 'لوفوكس', 'ميثيلفينيديت', 'ميرتازابين', 'ميلاتونين', 'ميثادون', 'نورتريبتيلين', 'نالتريكسون', 'هالوبيريدول', 'هالدول', 'هيدروكسيزين', 'ويلبوترين', 'حبوب السعادة', 'مهدئات', 'منومات', 'مضادات الاكتئاب', 'مضادات القلق', 'مضادات الذهان', 'مثبتات المزاج', 'أدوية نفسية', 'ادوية نفسية', 'حبوب نفسية', 'حبوب مهدئة', 'حبوب منومة', 'علاج نفسي دوائي', 'abilfy', 'abilify', 'acamprosate', 'agomelatine', 'alprazolam', 'alprzolam', 'amitriptilin', 'amitriptyline', 'anafranil', 'aripiprazole', 'asenapine', 'ativan', 'atomoxetin', 'atomoxetine', 'brexpiprazole', 'bromazepam', 'buprenorphine', 'bupropion', 'buproprion', 'busparon', 'buspirone', 'carbamazepine', 'carbamezapine', 'cariprazine', 'celexa', 'chlorpromazin', 'chlorpromazine', 'cipralex', 'cipralix', 'citalopram', 'citaloprom', 'clomipramin', 'clomipramine', 'clonazepam', 'clonazpam', 'clozapin', 'clozapine', 'cymbalta', 'depakine', 'desvenlafaxine', 'desvenlaflaxin', 'dexamfetamine', 'dexamphetamine', 'diazapam', 'diazepam', 'disulfiram', 'dogmatil', 'doxepin', 'duloxetin', 'duloxetine', 'effexor', 'escitalopram', 'eszopiclone', 'eszopicolone', 'etizolam', 'faverin', 'fluanxol', 'fluoxetin', 'fluoxetine', 'flupentixol', 'fluphenazine', 'fluvoxamine', 'gabapantine', 'gabapentin', 'guanfacine', 'haldol', 'haloperidol', 'halopridol', 'hydroxizin', 'hydroxyzine', 'imipramine', 'intuniv', 'invega', 'lamictal', 'lamotregen', 'lamotrigine', 'largactil', 'latuda', 'leponex', 'lexotanil', 'lis-dexamfetamine', 'lisdexamfetamine', 'lithium', 'lithyum', 'lorazepam', 'lorazpam', 'lurasidon', 'lurasidone', 'luvox', 'lyrica', 'melatonin', 'melatonine', 'methadone', 'methylphenidate', 'methyphenidate', 'mirtazapin', 'mirtazapine', 'modafinil', 'naltrexone', 'nortriptyline', 'olanzapin', 'olanzapine', 'oxcarbazepine', 'paliperidon', 'paliperidone', 'paroxetin', 'paroxetine', 'perphenazine', 'prazocin', 'prazosin', 'pregabalin', 'pregablin', 'pristiq', 'propanolol', 'propranolol', 'prozac', 'quetiapine', 'quetipine', 'remeron', 'rexulti', 'risperdal', 'risperidon', 'risperidone', 'ritalin', 'rivotril', 'saphris', 'sebralex', 'seroquel', 'seroxat', 'sertralin', 'sertraline', 'stilnox', 'strattera', 'sulpiride', 'tegretol', 'thioridazine', 'tofranil', 'topiramat', 'topiramate', 'trazadon', 'trazodone', 'trileptal', 'trintellix', 'valdoxan', 'valium', 'valporate', 'valproate', 'venlafaxine', 'venlaflaxin', 'vortioxetine', 'vraylar', 'vyvanse', 'wellbutrin', 'xanax', 'ziprasidon', 'ziprasidone', 'zoloft', 'zolpediem', 'zolpidem', 'zopiclone', 'zuclopenthixol', 'zyprexa']
MENTAL_HEALTH_KEYWORDS = CONDITION_KEYWORDS + FEMININE_KEYWORDS + MEDICATION_KEYWORDS


# Compile regex patterns for better performance
keyword_patterns = []
for keyword in MENTAL_HEALTH_KEYWORDS:
    try:
        if ' ' in keyword:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        else:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        keyword_patterns.append((keyword, pattern))
    except Exception as e:
        logger.print_warning(f"Could not compile pattern for keyword '{keyword}': {str(e)}")

def contains_mental_health_keywords(text):
    """Check if text contains any mental health keywords"""
    if not text or pd.isna(text) or not isinstance(text, str):
        return False

    try:
        for keyword, pattern in keyword_patterns:
            if pattern.search(text):
                return True
    except Exception:
        pass  # Silently fail for regex errors
    return False

def get_mental_health_matches(text):
    """Extract all mental health keywords found in text"""
    if not text or pd.isna(text) or not isinstance(text, str):
        return []

    matches = []
    try:
        for keyword, pattern in keyword_patterns:
            if pattern.search(text):
                matches.append(keyword)
    except Exception:
        pass  # Silently fail for regex errors
    return matches

# ===============================
# Initialize Metrics
# ===============================
metrics = {
    'total_posts': 0,
    'undefined_posts': 0,
    'removed_posts': 0,
    'short_posts': 0,
    'arabic_posts': 0,
    'non_arabic_posts': 0,
    'mental_health_arabic': 0,
    'mental_health_non_arabic': 0,
}

# Lists for storing data
clean_word_counts = []
non_arabic_word_counts = []
mental_health_keyword_counter = Counter()
mental_health_samples = []
clean_posts = {}
non_arabic_posts_map = {}

include_props = ['score', 'selftext', 'id', 'over_18', 'subreddit', 'title', 'created_utc']
include_props = [prop for prop in include_props if prop in df.columns]

# ===============================
# Helper Functions
# ===============================
def clean_text(text):
    """Basic cleaning with error handling."""
    if not isinstance(text, str):
        return ""
    try:
        text = re.sub(r"http\S+", "", text)  # remove URLs
        text = re.sub(r"\s+", " ", text)     # remove extra spaces
        return text.strip()
    except Exception:
        return str(text).strip()

def word_count(text):
    """Safely count words."""
    if not isinstance(text, str):
        return 0
    return len(text.split())

def arabic_ratio(text):
    """Calculate Arabic character ratio safely."""
    if not isinstance(text, str) or not text:
        return 0
    try:
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        return len(arabic_chars) / max(len(text), 1)
    except Exception:
        return 0

def is_arabic(text, ft_threshold=0.50, ratio_threshold=0.20):
    """Language detection with fallback."""
    if not isinstance(text, str) or not text:
        return False

    # Try FastText first if available
    if ft_model is not None:
        try:
            labels, probs = ft_model.predict(text.replace("\n", " ")[:1000], k=1)  # Limit text length
            lang = labels[0]
            confidence = probs[0]
            if lang == "__label__ar" and confidence >= ft_threshold:
                return True
        except Exception:
            pass  # Fall back to ratio method

    # Fallback to Arabic ratio
    ratio = arabic_ratio(text)
    return ratio >= ratio_threshold

# ===============================
# Main Processing Loop
# ===============================
logger.print_header("PROCESSING POSTS")

# Progress tracking
total_posts_to_process = len(df)
error_count = 0

for idx, (_, row) in enumerate(df.iterrows(), 1):
    try:
        metrics['total_posts'] += 1

        # Show progress
        extra_info = f"| Arabic: {metrics['arabic_posts']} | MH: {metrics['mental_health_arabic']}"
        logger.print_progress(idx, total_posts_to_process, extra_info)

        # Safely get text
        text = row.get('selftext', '')

        # 1️⃣ Undefined posts
        if pd.isna(text) or str(text).strip() == "":
            metrics['undefined_posts'] += 1
            continue

        text = str(text).strip()

        # 2️⃣ Removed posts
        if text.lower() == "[removed]":
            metrics['removed_posts'] += 1
            continue

        # Clean text
        text = clean_text(text)
        wc = word_count(text)

        # 3️⃣ Short posts
        if wc < 10:
            metrics['short_posts'] += 1
            continue

        # 4️⃣ Language detection
        try:
            if is_arabic(text):
                metrics['arabic_posts'] += 1
                clean_word_counts.append(wc)

                # Check for mental health keywords
                if contains_mental_health_keywords(text):
                    metrics['mental_health_arabic'] += 1
                    matches = get_mental_health_matches(text)
                    mental_health_keyword_counter.update(matches)

                    # Store sample (first 20 posts only)
                    if len(mental_health_samples) < 20:
                        mental_health_samples.append({
                            'id': row.get('id', 'N/A'),
                            'title': row.get('title', 'N/A')[:100],
                            'subreddit': row.get('subreddit', 'N/A'),
                            'text_preview': text[:200] + '...' if len(text) > 200 else text,
                            'keywords_found': matches[:5]  # Limit to first 5 keywords
                        })

                # Store clean post data
                post_data = {}
                for prop in include_props:
                    try:
                        post_data[prop] = row.get(prop, None)
                    except:
                        post_data[prop] = None
                clean_posts[row.get('id', f'unknown_{idx}')] = post_data

            else:
                metrics['non_arabic_posts'] += 1
                non_arabic_word_counts.append(wc)

                # Check for mental health keywords in non-Arabic posts
                if contains_mental_health_keywords(text):
                    metrics['mental_health_non_arabic'] += 1

                # Store non-Arabic post data
                post_data = {}
                for prop in include_props:
                    try:
                        post_data[prop] = row.get(prop, None)
                    except:
                        post_data[prop] = None
                non_arabic_posts_map[row.get('id', f'unknown_{idx}')] = post_data

        except Exception as e:
            error_count += 1
            if error_count <= 10:  # Show first 10 errors only
                logger.print_warning(f"Error processing post {idx}: {str(e)[:50]}")
            continue

    except Exception as e:
        error_count += 1
        if error_count <= 5:  # Show first 5 critical errors
            logger.print_error(f"Critical error at post {idx}: {str(e)}")
        continue

# Clear progress line and print completion
print()  # New line after progress bar
logger.print_success(f"Processing complete! Processed {metrics['total_posts']:,} posts with {error_count} errors")

# ===============================
# Reporting Metrics
# ===============================
logger.print_header("DATASET REPORT")

# Basic statistics
print(f"📊 Total posts processed: {metrics['total_posts']:,}")
print(f"📊 Undefined/empty posts: {metrics['undefined_posts']:,} ({metrics['undefined_posts']/metrics['total_posts']*100:.1f}%)")
print(f"📊 Removed posts: {metrics['removed_posts']:,} ({metrics['removed_posts']/metrics['total_posts']*100:.1f}%)")
print(f"📊 Short posts (<10 words): {metrics['short_posts']:,} ({metrics['short_posts']/metrics['total_posts']*100:.1f}%)")
print(f"📊 Valid Arabic posts (≥10 words): {metrics['arabic_posts']:,} ({metrics['arabic_posts']/metrics['total_posts']*100:.1f}%)")
print(f"📊 Valid Non-Arabic posts (≥10 words): {metrics['non_arabic_posts']:,} ({metrics['non_arabic_posts']/metrics['total_posts']*100:.1f}%)")

# Word statistics
if clean_word_counts:
    print("\n📊 Arabic Posts Word Statistics:")
    print(f"  📈 Average: {sum(clean_word_counts)/len(clean_word_counts):.1f} words")
    print(f"  📈 Median: {sorted(clean_word_counts)[len(clean_word_counts)//2] if clean_word_counts else 0} words")
    print(f"  📈 Max: {max(clean_word_counts):,} words")
    print(f"  📈 Min: {min(clean_word_counts)} words")
    print(f"  📈 Total words: {sum(clean_word_counts):,}")

if non_arabic_word_counts:
    print("\n📊 Non-Arabic Posts Word Statistics:")
    print(f"  📈 Average: {sum(non_arabic_word_counts)/len(non_arabic_word_counts):.1f} words")
    print(f"  📈 Median: {sorted(non_arabic_word_counts)[len(non_arabic_word_counts)//2] if non_arabic_word_counts else 0} words")
    print(f"  📈 Max: {max(non_arabic_word_counts):,} words")
    print(f"  📈 Min: {min(non_arabic_word_counts)} words")
    print(f"  📈 Total words: {sum(non_arabic_word_counts):,}")

# ===============================
# Mental Health Report
# ===============================
logger.print_header("MENTAL HEALTH MENTIONS REPORT")

total_mh = metrics['mental_health_arabic'] + metrics['mental_health_non_arabic']
print(f"🧠 Total posts mentioning mental health: {total_mh:,}")

if metrics['arabic_posts'] > 0:
    mh_arabic_pct = (metrics['mental_health_arabic'] / metrics['arabic_posts']) * 100
    print(f"🧠 Arabic MH posts: {metrics['mental_health_arabic']:,} ({mh_arabic_pct:.1f}% of Arabic posts)")
else:
    print(f"🧠 Arabic MH posts: 0")

if metrics['non_arabic_posts'] > 0:
    mh_non_pct = (metrics['mental_health_non_arabic'] / metrics['non_arabic_posts']) * 100
    print(f"🧠 Non-Arabic MH posts: {metrics['non_arabic_posts']:,} ({mh_non_pct:.1f}% of non-Arabic posts)")
else:
    print(f"🧠 Non-Arabic MH posts: 0")

# Top mental health keywords
if mental_health_keyword_counter:
    print("\n📊 Top Mental Health Keywords:")
    total_mentions = sum(mental_health_keyword_counter.values())
    for keyword, count in mental_health_keyword_counter.most_common(10):
        percentage = (count / total_mentions) * 100
        bar = '█' * int(percentage / 2)  # Simple bar chart
        print(f"  {keyword:20} : {count:4} ({percentage:4.1f}%) {bar}")

# Samples of mental health posts
if mental_health_samples:
    print("\n" + "="*70)
    print("🔍 SAMPLES OF MENTAL HEALTH POSTS (first 20)")
    print("="*70)
    for i, sample in enumerate(mental_health_samples, 1):
        print(f"\n{i}. ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   🆔 Post ID: {sample['id']}")
        print(f"   📌 Subreddit: r/{sample['subreddit']}")
        print(f"   📝 Title: {sample['title']}")
        print(f"   🔑 Keywords: {', '.join(sample['keywords_found'])}")
        print(f"   💬 Preview: {sample['text_preview']}")
else:
    print("\n📭 No mental health posts found in the sample.")

# Final summary
logger.print_header("SUMMARY")
print(f"✅ Successfully processed {metrics['total_posts']:,} posts")
print(f"✅ Mental health discussions: {total_mh:,} posts")
print(f"⚠️  Errors encountered: {error_count}")

# Execution time
logger.print_final()
print("\n" + "="*70)

# ===============================
# Save processed data to CSV
# ===============================
logger.print_header("SAVING PROCESSED DATA")

output_dir = '/content/drive/My Drive/CaRMA/'

# Save Arabic posts
if clean_posts:
    df_arabic_posts = pd.DataFrame.from_dict(clean_posts, orient='index')
    df_arabic_posts.index.name = 'post_id'
    arabic_output_path = os.path.join(output_dir, 'reddit_arabic_posts_cleaned.csv')
    df_arabic_posts.to_csv(arabic_output_path, index=True)
    logger.print_success(f"Clean Arabic posts saved to {arabic_output_path}")
else:
    logger.print_warning("No clean Arabic posts to save.")

# Save Non-Arabic posts
if non_arabic_posts_map:
    df_non_arabic_posts = pd.DataFrame.from_dict(non_arabic_posts_map, orient='index')
    df_non_arabic_posts.index.name = 'post_id'
    non_arabic_output_path = os.path.join(output_dir, 'reddit_non_arabic_posts_cleaned.csv')
    df_non_arabic_posts.to_csv(non_arabic_output_path, index=True)
    logger.print_success(f"Clean Non-Arabic posts saved to {non_arabic_output_path}")
else:
    logger.print_warning("No non-Arabic posts to save.")
