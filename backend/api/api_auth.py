import os
from functools import wraps

import jwt
import requests
from flask import jsonify, request

TENANT_ID = os.getenv("TENANT_ID")
AUDIENCE = os.getenv("AUDIENCE")
JWKS_URL = os.getenv("JWKS_URL")


def get_signing_key(kid):
    jwks = requests.get(JWKS_URL).json()["keys"]
    for key in jwks:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            unverified_header = jwt.get_unverified_header(token)
            key = get_signing_key(unverified_header["kid"])
            decoded = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                audience=AUDIENCE,
            )
            request.user = decoded
        except Exception as e:
            print("JWT decode error:", str(e))  # log error
            return jsonify({"error": "Token is invalid"}), 401

        return f(*args, **kwargs)

    return decorated
