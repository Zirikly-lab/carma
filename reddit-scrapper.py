import requests
import time
import csv
import re
from datetime import datetime

def is_arabic_text(text, threshold=0.6):
    """Simple Arabic detection by character ratio"""
    if not text:
        return False
    
    # Count Arabic characters (Unicode range 0600-06FF)
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    total_chars = sum(1 for c in text if not c.isspace())
    
    if total_chars == 0:
        return False
    
    return (arabic_chars / total_chars) >= threshold

def scrape_arabic(subreddit, max_posts=500, arabic_threshold=0.05, min_words=3, delay=0.5):
    """Scrape Arabic posts with simple logging"""
    
    output_file = f"{subreddit}/{subreddit}_arabic.csv"
    checkpoint = f"{subreddit}/{subreddit}_temp.csv"
    
    # ensure checkpoint directory exists
    import os
    os.makedirs(subreddit, exist_ok=True)

    # Initialize CSV
    with open(checkpoint, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'author', 'created_utc', 'subreddit', 'title', 'text', 'arabic_ratio'])
    
    saved = 0
    after = None
    batch_num = 0
    
    print(f"\n📁 r/{subreddit} | Target: {max_posts} Arabic posts")
    
    while saved < max_posts:
        # Fetch batch
        params = {"subreddit": subreddit, "limit": 100, "sort": "desc", "fields": "id,title,selftext,created_utc,author"}
        if after:
            params["after"] = after
        
        try:
            resp = requests.get("https://arctic-shift.photon-reddit.com/api/posts/search", params=params, timeout=30)
            resp.raise_for_status()
            posts = resp.json().get('data', [])
            
            if not posts:
                print(f"🏁 No more posts")
                break
            
            # Process batch
            included = 0
            excluded = 0
            
            with open(checkpoint, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                for post in posts:
                    text = post.get('selftext', '') or post.get('title', '')
                    ratio = sum(1 for c in text if '\u0600' <= c <= '\u06FF') / max(1, len([c for c in text if not c.isspace()]))
                    
                    # Check if Arabic
                    if (ratio >= arabic_threshold and 
                        len(re.findall(r'[\u0600-\u06FF]{2,}', text)) >= min_words and
                        post.get('author') != '[deleted]'):
                        
                        writer.writerow([
                            post.get('id', ''),
                            post.get('author', ''),
                            post.get('created_utc', 0),
                            subreddit,
                            post.get('title', '')[:100],
                            text[:1000] if text else '',
                            round(ratio, 2)
                        ])
                        included += 1
                        saved += 1
                    else:
                        excluded += 1
                    
                    after = post.get('created_utc')
                    
                    if saved >= max_posts:
                        break
            
            batch_num += 1
            print(f"   Batch {batch_num}: ✅ {included} included | ❌ {excluded} excluded (total: {saved}/{max_posts})")
            
            if saved >= max_posts:
                break
            
            time.sleep(delay)
            
        except Exception as e:
            print(f"   Error: {e}")
            break
    
    # Finalize
    import os
    if saved > 0:
        # ensure folder directory exists


        os.makedirs(subreddit, exist_ok=True)
    
        os.rename(checkpoint, output_file)
        print(f"✅ Done! Saved {saved} Arabic posts to {output_file}")
    else:
        os.remove(checkpoint)
        print(f"⚠️ No Arabic posts found")
    
    return saved

# ============= RUN =============

if __name__ == "__main__":
    arabic_subreddits = ["saudi_arabia", "egypt", "jordan", "uae", "arabs"]
    
    for sub in arabic_subreddits:
        scrape_arabic(sub, max_posts=300, arabic_threshold=0.4, min_words=3, delay=0.5)
    
    print("\n🎉 All done!")