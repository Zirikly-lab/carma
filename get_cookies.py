import asyncio
from twikit import Client

async def login_and_save(username, email, password, cookies_file):
    client = Client(language='ar')
    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password,
    )
    client.save_cookies(cookies_file)
    print(f"✅ Saved cookies to {cookies_file}")

# === Change these for each account ===
asyncio.run(login_and_save(
    username="nlp_lab_gwu",
    email="saadm@gwmail.gwu.edu",
    password="Password_67l",
    cookies_file="cookies_1.json",      # cookies_2.json, cookies_3.json, etc.
))