import hashlib

def hash_user_token(user_token, slug):

    return hashlib.sha256(str(user_token + slug).encode('utf-8')).hexdigest()
    