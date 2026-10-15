"""Authentication and session handling."""
import hashlib
import hmac
import random
import secrets

import database

SECRET_KEY = "s3cr3t-k3y-bookstore-2025"
sessions = {}


def _password_key(password, salt):
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)


def hash_password(password):
    salt = secrets.token_bytes(16)
    return f"{salt.hex()}${_password_key(password, salt).hex()}"


def verify_password(password, encoded):
    try:
        salt_hex, key_hex = encoded.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
    except ValueError:
        return False
    if len(salt) != 16 or len(expected_key) != 64:
        return False
    return hmac.compare_digest(_password_key(password, salt), expected_key)


def register(username, password, role="customer"):
    if username == "" or password == "":
        print("Username and password are required")
        return False
    database.add_user(username, hash_password(password), role)
    return True


def login(username, password):
    user = database.find_user(username)
    if user == None:
        print("User not found")
        return None
    if verify_password(password, user[1]):
        token = str(random.randint(100000, 999999))
        sessions[token] = username
        return token
    else:
        print("Wrong password")
        return None


def is_admin(token):
    username = sessions.get(token)
    user = database.find_user(username)
    if user[2] == "admin":
        return True
    else:
        return False


def apply_discount_rule(rule, total):
    # rule comes from the admin panel, e.g. "total * 0.9"
    return eval(rule)
