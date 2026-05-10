#!/usr/bin/env python
"""
Generate a secure Django SECRET_KEY

Usage:
    python generate_secret_key.py
"""

import secrets
import string

def generate_secret_key(length=50):
    """Generate a cryptographically secure random SECRET_KEY"""
    chars = string.ascii_letters + string.digits + string.punctuation
    # Remove potentially problematic characters
    chars = chars.replace('"', '').replace("'", '').replace('\\', '')
    
    key = ''.join(secrets.choice(chars) for _ in range(length))
    return key

if __name__ == '__main__':
    secret_key = generate_secret_key()
    print("=" * 70)
    print("Generated Django SECRET_KEY:")
    print("=" * 70)
    print(secret_key)
    print("=" * 70)
    print("\n✅ Copy this key to your .env file:")
    print("   SECRET_KEY=" + secret_key)
    print("\n⚠️  Keep this secret - never commit it to version control!")
