#!/usr/bin/env python3
"""Test REGPRO5 REG function"""

from source.REGPRO5 import REGPRO5

# Test with a valid cookie
cookie = "c_user=100082148649666; xs=29:-LkIMdyeIRgcBQ:2:1774461197:-1:-1; fr=0R1GY8u8iC5i45qlN.AWe-1qzjZBYZ8hQnpwPV9kbtvkH3FBJbOgOdnu7dx6w7635WEyQ.BpxCEN..AAA.0.0.BpxCEN.AWc3vDGe-FDZf6Q7YZOLeMfm-3Y; datr=DSHEaU4rgjP7-XgjkmZ14Iaq"

reg = REGPRO5(cookie)

print("[1] Testing login...")
if reg.login():
    print("[✔] Login successful")
    print(f"    token: {reg.session.token[:50]}...")
    print(f"    user_id: {reg.session.user_id}")
else:
    print("[✘] Login failed")
    exit(1)

print("\n[2] Testing REG...")
result = reg.REG("Test bio", "Test Page Name")
print(f"Result: {result}")

if result.get("ok"):
    print(f"[✔] REG Success - Page ID: {result.get('page_id')}")
else:
    print(f"[✘] REG Failed - Error: {result.get('error')}")
