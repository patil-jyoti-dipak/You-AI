import hashlib, time, html, re
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import JWTError, jwt
from collections import defaultdict

SECRET_KEY = "you2ai-secret-2025-hackathon"
ALGORITHM = "HS256"
_rate = defaultdict(list)

def check_rate_limit(ip, limit=30, window=60):
    now = time.time()
    _rate[ip] = [t for t in _rate[ip] if now - t < window]
    if len(_rate[ip]) >= limit:
        raise HTTPException(429, "Too many requests. Wait a moment.")
    _rate[ip].append(now)

def create_token(session_id):
    payload = {"sub": session_id, "exp": datetime.utcnow() + timedelta(hours=2)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sid = data.get("sub")
        if not sid:
            raise HTTPException(401, "Invalid token")
        return sid
    except JWTError:
        raise HTTPException(401, "Session expired. Please rebuild your twin.")

def clean(text):
    bad = ["ignore previous instructions", "ignore all instructions",
           "jailbreak", "<script", "javascript:", "eval(", "exec("]
    t = html.escape(text)
    for b in bad:
        if b in t.lower():
            raise HTTPException(400, "Input contains harmful content.")
    return t.strip()

def clean_list(items):
    return [clean(i) for i in items]

def new_session_id(ip=""):
    return hashlib.sha256(f"{ip}{time.time()}you2ai".encode()).hexdigest()[:32]