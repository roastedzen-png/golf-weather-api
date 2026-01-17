#!/usr/bin/env python3
"""
Generate API keys for clients.

Usage:
    python scripts/generate_api_key.py <client_name>

Example:
    python scripts/generate_api_key.py inrange_prod
    python scripts/generate_api_key.py inrange_test
    python scripts/generate_api_key.py admin
"""

import secrets
import hashlib
import sys


def generate_api_key(client_name: str) -> tuple:
    """
    Generate a secure API key for a client.

    Args:
        client_name: Name of the client (e.g., inrange_prod)

    Returns:
        Tuple of (raw_key, key_hash)
    """
    # Generate a secure random key with prefix
    raw_key = f"gw_{client_name}_{secrets.token_hex(24)}"

    # Hash it for storage
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    return raw_key, key_hash


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_api_key.py <client_name>")
        print("Example: python generate_api_key.py inrange_prod")
        sys.exit(1)

    client_name = sys.argv[1].lower().replace("-", "_")
    raw_key, key_hash = generate_api_key(client_name)

    print()
    print("=" * 70)
    print(f"API Key Generated for: {client_name}")
    print("=" * 70)
    print()
    print("GIVE THIS TO THE CLIENT (SECRET - only show once):")
    print(f"  {raw_key}")
    print()
    print("ADD THIS TO RAILWAY ENVIRONMENT VARIABLES:")
    print(f"  APIKEY_{client_name.upper()}={key_hash}")
    print()
    if client_name == "admin":
        print("ALSO ADD AS ADMIN KEY (for /admin/* endpoints):")
        print(f"  ADMIN_KEY_HASH={key_hash}")
        print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
