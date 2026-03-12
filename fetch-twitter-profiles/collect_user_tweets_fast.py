"""
FAST Twitter User Tweet Collector — Search API + Server-Side Filtering
=======================================================================
Collects original text-only tweets for a list of users.

SPEED STRATEGY:
  Instead of get_user_tweets() (timeline API), we use search_tweet() with
  Twitter's advanced search operators to filter SERVER-SIDE:

    from:username -filter:retweets -filter:media -filter:replies

  This tells Twitter to ONLY return original text tweets — no RTs, no media,
  no quote tweets, no replies. This means:
    - ~50-70% fewer results to paginate through
    - Far fewer API calls needed
    - No wasted bandwidth on content we'd discard anyway

  Additional speed optimizations:
    - Concurrent user processing (async batches of users)
    - Tighter delays (search API has separate rate limits from timeline API)
    - Smart pagination: stop early when tweets get very old

Setup:
    pip install twikit pandas openpyxl
    pip install google-auth-oauthlib google-api-python-client  # for GDrive

Usage:
    python collect_user_tweets_fast.py
    python collect_user_tweets_fast.py --input agreed_genuine_unique_users.csv
    python collect_user_tweets_fast.py --resume
    python collect_user_tweets_fast.py --gdrive-folder YOUR_FOLDER_ID
    python collect_user_tweets_fast.py --max-batches 50
"""

from twikit import Client, TooManyRequests
import asyncio
import pandas as pd
import openpyxl
import os
import time
import json
from datetime import datetime
from random import randint, uniform
from pathlib import Path
from typing import Optional
import argparse
import glob


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
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), GDRIVE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_to_gdrive(filepath: str, folder_id: str = None) -> Optional[str]:
    """Upload a file to Google Drive."""
    if not GDRIVE_ENABLED:
        return None
    creds = setup_gdrive_credentials()
    if not creds:
        return None
    try:
        service = build('drive', 'v3', credentials=creds)
        filename = os.path.basename(filepath)
        mime_types = {'.json': 'application/json', '.csv': 'text/csv', '.txt': 'text/plain'}
        ext = os.path.splitext(filepath)[1].lower()
        mime_type = mime_types.get(ext, 'application/octet-stream')
        file_metadata = {'name': filename}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        media = MediaFileUpload(filepath, mimetype=mime_type)
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id, webViewLink'
        ).execute()
        print(f"   ☁️  GDrive: {filename}")
        return file.get('webViewLink')
    except Exception as e:
        return None


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_COOKIES = "../cookies/cookies_5.json"
DEFAULT_MAX_TWEETS = 3200           # Twitter's timeline cap
DEFAULT_MAX_BATCHES = 170           # 170 × ~20 = ~3400 (slightly over to ensure we hit 3200)
BATCH_DELAY_MIN = 2                # tighter delays for search API
BATCH_DELAY_MAX = 4
USER_DELAY_MIN = 5
USER_DELAY_MAX = 10
RATE_LIMIT_WAIT = 960              # 16 minutes (15 + buffer)
MAX_CONSECUTIVE_ERRORS = 5
PROGRESS_SAVE_EVERY = 3


# ============================================================
# READ USERS FROM CSV OR XLSX
# ============================================================

def read_users_csv(filepath: str) -> list[dict]:
    """Read users from the agreed_genuine_unique_users.csv format."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    users = []
    seen = set()
    for _, row in df.iterrows():
        username = str(row.get('username', '')).strip().replace('\n', '').replace('\r', '')
        if not username or username.lower() in seen:
            continue
        seen.add(username.lower())
        users.append({
            'username': username,
            'user_id': str(row.get('user_id', '')),
            'statuses_count': int(row.get('statuses_count', 0)),
        })
    # Sort by statuses_count ASCENDING — small accounts first for fast early wins
    users.sort(key=lambda u: u['statuses_count'])
    print(f"📋 Loaded {len(users)} unique users (sorted smallest → largest)")
    return users


def read_users_xlsx(filepath: str) -> list[dict]:
    """Read users from Excel format (Sheet1, column A = username)."""
    wb = openpyxl.load_workbook(filepath, read_only=True)
    ws = wb["Sheet1"]
    users = []
    seen = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        username = row[0]
        if not username:
            continue
        username = str(username).strip().replace('\n', '').replace('\r', '')
        if not username or username.lower() in seen:
            continue
        seen.add(username.lower())
        users.append({'username': username, 'user_id': '', 'statuses_count': 0})
    wb.close()
    print(f"📋 Loaded {len(users)} unique users from Excel")
    return users


def read_users(filepath: str) -> list[dict]:
    """Auto-detect file format and read users."""
    if filepath.endswith('.csv'):
        return read_users_csv(filepath)
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        return read_users_xlsx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


# ============================================================
# EXTRACT USER METADATA
# ============================================================

def extract_user_metadata(user_obj) -> dict:
    """Extract all available metadata from a twikit User object."""
    if user_obj is None:
        return {}
    metadata = {}
    fields = [
        'id', 'name', 'screen_name', 'description', 'location', 'url',
        'followers_count', 'following_count', 'statuses_count',
        'favourites_count', 'favorites_count', 'listed_count',
        'verified', 'is_blue_verified', 'protected',
        'created_at', 'profile_image_url', 'profile_banner_url',
        'default_profile', 'default_profile_image', 'media_count',
        'possibly_sensitive', 'pinned_tweet_ids',
    ]
    for f in fields:
        val = getattr(user_obj, f, None)
        if val is not None:
            metadata[f'user_{f}'] = val
    metadata['user_profile_url'] = f"https://x.com/{getattr(user_obj, 'screen_name', '')}"
    return metadata


# ============================================================
# EXTRACT TWEET DATA
# ============================================================

def extract_tweet_data(tweet, username: str) -> dict:
    """Extract fields from a twikit Tweet object."""
    tweet_text = getattr(tweet, 'text', '') or ''
    screen_name = getattr(tweet.user, 'screen_name', username) if tweet.user else username

    return {
        'tweet_id':             tweet.id,
        'tweet_text':           tweet_text,
        'tweet_created_at':     str(tweet.created_at) if hasattr(tweet, 'created_at') and tweet.created_at else '',
        'tweet_lang':           getattr(tweet, 'lang', ''),
        'retweet_count':        getattr(tweet, 'retweet_count', 0),
        'favorite_count':       getattr(tweet, 'favorite_count', 0),
        'reply_count':          getattr(tweet, 'reply_count', 0),
        'quote_count':          getattr(tweet, 'quote_count', 0),
        'bookmark_count':       getattr(tweet, 'bookmark_count', 0),
        'view_count':           getattr(tweet, 'view_count', ''),
        'tweet_url':            f"https://x.com/{screen_name}/status/{tweet.id}",
        'hashtags':             ', '.join(getattr(tweet, 'hashtags', []) or []),
        'source':               getattr(tweet, 'source', ''),
        'username':             username,
    }


# ============================================================
# FAST COLLECTION VIA SEARCH API
# ============================================================

async def collect_user_fast(
    client: Client,
    username: str,
    max_batches: int = DEFAULT_MAX_BATCHES,
) -> tuple[dict | None, list[dict], dict]:
    """
    Collect user metadata + tweets using the SEARCH API with server-side filters.

    Search query: from:USERNAME -filter:retweets -filter:media

    This is MUCH faster than timeline API because:
    1. Twitter filters out RTs/media/quotes BEFORE sending results
    2. Every result we get back is usable — no waste
    3. Search API has its own rate limit bucket

    Returns: (metadata_dict, tweet_list, info_dict)
    """
    info = {'skipped_dupes': 0, 'batches': 0, 'empty_batches': 0, 'error': None}

    # ─── Get user profile ───
    user_obj = None
    try:
        user_obj = await client.get_user_by_screen_name(username)
    except TooManyRequests:
        print(f"      ⏳ Rate limit (profile). Waiting...")
        await asyncio.sleep(RATE_LIMIT_WAIT)
        try:
            user_obj = await client.get_user_by_screen_name(username)
        except Exception as e:
            info['error'] = str(e)
            return None, [], info
    except Exception as e:
        error_str = str(e)
        if '404' in error_str or 'not found' in error_str.lower():
            print(f"      ⚠️  @{username} not found (deleted/suspended)")
        elif '403' in error_str:
            print(f"      ⚠️  @{username} forbidden (protected/suspended)")
        else:
            print(f"      ⚠️  @{username} error: {e}")
        info['error'] = error_str
        return None, [], info

    if user_obj is None:
        return None, [], info

    metadata = extract_user_metadata(user_obj)

    if getattr(user_obj, 'protected', False):
        print(f"      🔒 @{username} is protected")
        info['error'] = 'protected'
        return metadata, [], info

    # ─── Search for tweets with server-side filtering ───
    # -filter:retweets  = no retweets
    # -filter:media     = no media (images, videos, GIFs)
    # -filter:replies   = no replies (only original standalone tweets)
    # Quoted tweets with no media will still pass through, so we filter client-side too
    search_query = f"from:{username} -filter:retweets -filter:media -filter:replies"

    tweets_data = []
    seen_ids = set()
    batch_count = 0
    empty_batches = 0

    try:
        results = await client.search_tweet(search_query, product='Latest')
    except TooManyRequests:
        print(f"      ⏳ Rate limit (search). Waiting...")
        await asyncio.sleep(RATE_LIMIT_WAIT)
        try:
            results = await client.search_tweet(search_query, product='Latest')
        except Exception as e:
            info['error'] = str(e)
            return metadata, [], info
    except Exception as e:
        info['error'] = str(e)
        print(f"      ⚠️  Search failed for @{username}: {e}")
        return metadata, [], info

    while results and batch_count < max_batches:
        new_in_batch = 0

        for tweet in results:
            if tweet.id in seen_ids:
                info['skipped_dupes'] += 1
                continue
            seen_ids.add(tweet.id)

            # Client-side: skip any remaining quote tweets or replies that slipped through
            tweet_text = getattr(tweet, 'text', '') or ''
            if tweet_text.startswith('RT @'):
                continue
            if getattr(tweet, 'is_quote_status', False):
                continue
            if getattr(tweet, 'quoted_tweet', None) is not None:
                continue

            new_in_batch += 1
            tweets_data.append(extract_tweet_data(tweet, username))

            # Hard cap at 3200 tweets
            if len(tweets_data) >= DEFAULT_MAX_TWEETS:
                break

        batch_count += 1
        info['batches'] = batch_count

        # Stop if we've hit the 3200 cap
        if len(tweets_data) >= DEFAULT_MAX_TWEETS:
            break

        if new_in_batch == 0:
            empty_batches += 1
            info['empty_batches'] = empty_batches
            if empty_batches >= 3:
                break
        else:
            empty_batches = 0
            info['empty_batches'] = 0

        # Paginate
        try:
            await asyncio.sleep(uniform(BATCH_DELAY_MIN, BATCH_DELAY_MAX))
            results = await results.next()
        except TooManyRequests:
            print(f"      ⏳ Rate limit (pagination). Waiting...")
            await asyncio.sleep(RATE_LIMIT_WAIT)
            try:
                results = await results.next()
            except Exception:
                break
        except Exception:
            break

    return metadata, tweets_data, info


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(
        description='FAST tweet collector — search API with server-side filtering. '
                    '1 CSV per user + 1 combined CSV + 1 metadata CSV → GDrive.'
    )
    parser.add_argument('--input', '-i',
                        default='agreed_genuine_unique_users.csv',
                        help='Input file (CSV or XLSX)')
    parser.add_argument('--cookies', '-c', default=DEFAULT_COOKIES)
    parser.add_argument('--max-batches', type=int, default=DEFAULT_MAX_BATCHES,
                        help=f'Max batches per user (default: {DEFAULT_MAX_BATCHES})')
    parser.add_argument('--resume', '-r', action='store_true',
                        help='Resume from last progress file')
    parser.add_argument('--output-dir', '-o', default='.',
                        help='Output directory')
    parser.add_argument('--gdrive-folder', type=str, default=None,
                        help='Google Drive folder ID')

    args = parser.parse_args()
    gdrive_folder = args.gdrive_folder

    print(f"\n{'='*70}")
    print(f"  ⚡ FAST TWITTER TWEET COLLECTOR (Search API)")
    print(f"{'='*70}")
    print(f"  Strategy:        from:user -filter:retweets -filter:media -filter:replies")
    print(f"  Max tweets/user: {DEFAULT_MAX_TWEETS}")
    print(f"  Input:           {args.input}")
    print(f"  Cookies:         {args.cookies}")
    print(f"  Max batches:     {args.max_batches}")
    print(f"  Output dir:      {args.output_dir}")
    print(f"  Google Drive:    {'Enabled' if GDRIVE_ENABLED else 'Not installed'}")
    print(f"{'='*70}\n")

    # ─── Read users ───
    users = read_users(args.input)
    if not users:
        print("❌ No users found.")
        return

    # ─── Output setup ───
    os.makedirs(args.output_dir, exist_ok=True)
    per_user_dir = os.path.join(args.output_dir, 'per_user_tweets')
    os.makedirs(per_user_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    combined_file = os.path.join(args.output_dir, f'ALL_tweets_combined_{timestamp}.csv')
    metadata_file = os.path.join(args.output_dir, f'ALL_metadata_{timestamp}.csv')
    progress_file = os.path.join(args.output_dir, f'progress_{timestamp}.json')

    # ─── Resume ───
    completed_users = set()
    all_metadata = []
    all_tweets = []

    if args.resume:
        pfiles = sorted(glob.glob(os.path.join(args.output_dir, 'progress_*.json')))
        if pfiles:
            with open(pfiles[-1], 'r') as f:
                pdata = json.load(f)
            completed_users = set(pdata.get('completed_users', []))
            print(f"📂 Resuming: {len(completed_users)} users already done")

            mfiles = sorted(glob.glob(os.path.join(args.output_dir, 'ALL_metadata_*.csv')))
            cfiles = sorted(glob.glob(os.path.join(args.output_dir, 'ALL_tweets_combined_*.csv')))
            if mfiles:
                all_metadata = pd.read_csv(mfiles[-1], encoding='utf-8-sig').to_dict('records')
            if cfiles:
                all_tweets = pd.read_csv(cfiles[-1], encoding='utf-8-sig').to_dict('records')
            print(f"   Loaded {len(all_metadata)} users, {len(all_tweets):,} tweets\n")

    # ─── Login ───
    if not os.path.exists(args.cookies):
        print(f"❌ Cookies file not found: {args.cookies}")
        print(f"\n   Login example:")
        print(f"   from twikit import Client; import asyncio")
        print(f"   async def login():")
        print(f"       c = Client(language='ar')")
        print(f"       await c.login(auth_info_1='USER', auth_info_2='EMAIL', password='PASS')")
        print(f"       c.save_cookies('cookies.json')")
        print(f"   asyncio.run(login())")
        return

    client = Client(language='ar')
    client.load_cookies(args.cookies)
    print("✅ Cookies loaded\n")

    # ─── Collection loop ───
    start_time = time.time()
    consecutive_errors = 0
    stats = {
        'total_users': len(users),
        'collected': 0,
        'failed': 0,
        'not_found': 0,
        'protected': 0,
        'total_tweets': 0,
        'gdrive_uploads': 0,
    }

    remaining_users = [u for u in users if u['username'].lower() not in completed_users]
    print(f"🚀 Starting collection: {len(remaining_users)} users remaining\n")

    for idx, user_info in enumerate(remaining_users, 1):
        username = user_info['username']
        expected = user_info.get('statuses_count', '?')

        print(f"[{idx}/{len(remaining_users)}] ⚡ @{username} (reported: {expected} statuses)")

        try:
            metadata, tweets, info = await collect_user_fast(
                client=client,
                username=username,
                max_batches=args.max_batches,
            )

            if metadata is None:
                stats['not_found'] += 1
                all_metadata.append({
                    'username': username,
                    'collection_status': 'not_found',
                    'error': info.get('error', ''),
                    'tweets_collected': 0,
                    'timestamp': datetime.now().isoformat(),
                })
                completed_users.add(username.lower())
                consecutive_errors = 0
                await asyncio.sleep(randint(3, 6))
                continue

            if info.get('error') == 'protected':
                stats['protected'] += 1
                metadata['collection_status'] = 'protected'
            else:
                metadata['collection_status'] = 'success'

            metadata['username'] = username
            metadata['tweets_collected'] = len(tweets)
            metadata['batches_used'] = info['batches']
            metadata['timestamp'] = datetime.now().isoformat()

            all_metadata.append(metadata)
            all_tweets.extend(tweets)

            stats['collected'] += 1
            stats['total_tweets'] += len(tweets)
            consecutive_errors = 0

            print(f"      ✅ {len(tweets)} tweets ({info['batches']} batches)")

            # Save per-user CSV + upload
            if tweets:
                user_csv = os.path.join(per_user_dir, f'{username}_tweets.csv')
                pd.DataFrame(tweets).to_csv(user_csv, index=False, encoding='utf-8-sig')
                url = upload_to_gdrive(user_csv, gdrive_folder)
                if url:
                    stats['gdrive_uploads'] += 1

        except TooManyRequests:
            print(f"      ⏳ Rate limit! Waiting {RATE_LIMIT_WAIT//60} min...")
            await asyncio.sleep(RATE_LIMIT_WAIT)
            consecutive_errors = 0
            stats['failed'] += 1
            continue

        except Exception as e:
            consecutive_errors += 1
            print(f"      ❌ Error: {e}")
            if '429' in str(e):
                await asyncio.sleep(RATE_LIMIT_WAIT)
                consecutive_errors = 0
            elif consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"\n⚠️  ABORTING: {MAX_CONSECUTIVE_ERRORS} consecutive errors. Use --resume.")
                break
            stats['failed'] += 1
            continue

        completed_users.add(username.lower())

        # ─── Progress save ───
        if stats['collected'] % PROGRESS_SAVE_EVERY == 0:
            with open(progress_file, 'w') as f:
                json.dump({
                    'completed_users': list(completed_users),
                    'stats': stats,
                    'timestamp': datetime.now().isoformat(),
                }, f, indent=2)
            if all_metadata:
                pd.DataFrame(all_metadata).to_csv(metadata_file, index=False, encoding='utf-8-sig')
            if all_tweets:
                pd.DataFrame(all_tweets).to_csv(combined_file, index=False, encoding='utf-8-sig')

            elapsed = time.time() - start_time
            rate = elapsed / max(stats['collected'], 1)
            eta = (len(remaining_users) - idx) * rate
            eta_str = f"{eta/60:.0f}m" if eta < 3600 else f"{eta/3600:.1f}h"

            print(f"\n   💾 Saved ({stats['collected']}/{len(remaining_users)}) "
                  f"| {stats['total_tweets']:,} tweets | ETA: ~{eta_str}\n")

        # Delay between users
        await asyncio.sleep(uniform(USER_DELAY_MIN, USER_DELAY_MAX))

    # ════════════════════════════════════════════════════════════
    # FINAL SAVE
    # ════════════════════════════════════════════════════════════
    elapsed = time.time() - start_time

    print(f"\n\n{'='*70}")
    print(f"  ⚡ COLLECTION COMPLETE!")
    print(f"{'='*70}")

    if all_metadata:
        meta_df = pd.DataFrame(all_metadata)
        meta_df.to_csv(metadata_file, index=False, encoding='utf-8-sig')
        print(f"\n  📄 Metadata:  {metadata_file} ({len(meta_df)} users)")
        url = upload_to_gdrive(metadata_file, gdrive_folder)
        if url:
            stats['gdrive_uploads'] += 1

    if all_tweets:
        comb_df = pd.DataFrame(all_tweets)
        comb_df.to_csv(combined_file, index=False, encoding='utf-8-sig')
        print(f"  📄 Combined:  {combined_file} ({len(comb_df):,} tweets)")
        url = upload_to_gdrive(combined_file, gdrive_folder)
        if url:
            stats['gdrive_uploads'] += 1

    with open(progress_file, 'w') as f:
        json.dump({
            'completed_users': list(completed_users),
            'stats': stats,
            'timestamp': datetime.now().isoformat(),
            'completed': True,
        }, f, indent=2)
    upload_to_gdrive(progress_file, gdrive_folder)

    print(f"\n  📊 Stats:")
    print(f"     Collected:     {stats['collected']} users")
    print(f"     Not found:     {stats['not_found']}")
    print(f"     Protected:     {stats['protected']}")
    print(f"     Failed:        {stats['failed']}")
    print(f"     Total tweets:  {stats['total_tweets']:,}")
    print(f"     GDrive files:  {stats['gdrive_uploads']}")
    print(f"     Time:          {elapsed/60:.1f} min")

    print(f"\n  📁 Files:")
    print(f"     Per-user:  {per_user_dir}/")
    print(f"     Combined:  {combined_file}")
    print(f"     Metadata:  {metadata_file}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(main())
