#!/usr/bin/env python
"""
Secret Key Generator for Smart Seating Arrangement

This script generates a secure random key that can be used as a SECRET_KEY
in your .env file. Run this script to create a new key:

python generate_secret_key.py
"""
import os
import secrets
import string
import sys

def generate_secret_key(length=50):
    """Generate a secure random string for use as a SECRET_KEY."""
    # Use a mix of letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Main function to generate and display a secret key."""
    print("\n=== Secret Key Generator for Smart Seating Arrangement ===\n")
    
    try:
        # Get length from command line if provided
        length = int(sys.argv[1]) if len(sys.argv) > 1 else 50
        if length < 32:
            print("Warning: For security, a key length of at least 32 is recommended.")
            print("Using the requested length anyway...\n")
    except (ValueError, IndexError):
        length = 50
        print("Using default key length of 50 characters...\n")
    
    # Generate the key
    key = generate_secret_key(length)
    
    # Print the key
    print("Your new SECRET_KEY:")
    print(f"\n{key}\n")
    print("Add this to your .env file as:")
    print(f"SECRET_KEY={key}")
    print("\nKeep this key secure! Do not share it or commit it to version control.")

if __name__ == "__main__":
    main() 