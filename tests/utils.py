import jwt
from time import time


def make_jwt():
    return jwt.encode({"user_id": "A", "exp": time() + 24 * 60 * 60}, "NotSecret")
