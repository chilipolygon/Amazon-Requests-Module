# ---------------------
from http import cookiejar
import asyncio
from playwright.async_api import async_playwright
# --------------------
import os
import json
from colorama import Fore, init
from pprint import pprint
# ---------------------
init()
init(autoreset=True)
os.system('cls' if os.name == 'nt' else 'clear')
f = open('./appdata/config.json')
data = json.load(f)


# MUST HAVE PRIME
# MUST HAVE ONE CLICK
# MUST SELECT "Keep me signed in"
# MUST USE AGED ACCOUNT
# ====================================
# MUST HAVE THESE FOR BEST SUCCESS

async def session() -> None:
    print(Fore.MAGENTA + '[+] Launching Page')

    async with async_playwright() as s:
        browser = await s.chromium.launch(headless=False)
        page = await browser.new_page()
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        )
        await page.goto("https://smile.amazon.com/gp/sign-in.html")

        while page.is_closed() != True:
            await page.wait_for_timeout(5000)

        cookies = await page.context.cookies()
        cookies_json = {}

        for i, d in enumerate(cookies):
            cookies_json[i] = d

        session_name = input('Enter your session name: ')
        with open(f"./appdata/cookies.json", "w") as f:
            json.dump(cookies_json, f, indent=4)

        with open(f"./appdata/config.json", "r+") as f:
            data = json.load(f)
            data['account'] = session_name
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        await page.close()

asyncio.run(session())
