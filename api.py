import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from workflow import extract_persona, run_twin_workflow
from security import (check_rate_limit, create_session_token,
                       verify_session_token, sanitize_input,
                       sanitize_list, generate_session_id)

router = APIRouter(prefix="/api/v1")

# ── Simple in-memory session store ───────────────────────────
_sessions = {}

def save_session(sid, persona):
    _sessions[sid] = {"persona": persona, "created": time.time()}

def get_session(sid):
    entry = _sessions.get(sid)
    if not entry:
        return None
    if time.time() - entry["created"] > 7200:
        del _sessions[sid]
        return None
    return entry["persona"]

# ── Request schemas ───────────────────────────────────────────
class PersonaRequest(BaseModel):
    sample_texts: List[str]
    tone: str
    risk_level: str
    communication_style: str
    personality_type: str
    additional_traits: Optional[str] = ""

class ReplyRequest(BaseModel):
    session_id: str
    original_message: str
    context: Optional[str] = ""

class DecisionRequest(BaseModel):
    session_id: str
    situation: str
    options: List[str]
    constraints: Optional[str] = ""

class PlanRequest(BaseModel):
    session_id: str
    goal: str
    timeframe: str
    priorities: Optional[List[str]] = []

# ── Routes ────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "online", "service": "You² AI"}

@router.post("/persona/setup")
async def setup_persona(request: Request, payload: PersonaRequest):
    ip = request.client.host
    check_rate_limit(ip, limit=10, window=60)

    valid = [t.strip() for t in payload.sample_texts if len(t.strip()) >= 5]
    if len(valid) < 3:
        raise HTTPException(400, "Need at least 3 valid text samples (min 5 chars each).")

    clean = sanitize_list(valid)
    persona = extract_persona(
        clean, payload.tone, payload.risk_level,
        payload.communication_style, payload.personality_type,
        payload.additional_traits or ""
    )

    sid = generate_session_id(ip)
    save_session(sid, persona)
    token = create_session_token(sid)

    return {
        "session_id": token,
        "tone": persona.get("tone", payload.tone),
        "risk_level": persona.get("risk_level", payload.risk_level),
        "communication_style": persona.get("communication_style", payload.communication_style),
        "personality_type": persona.get("personality_type", payload.personality_type),
        "traits": persona.get("traits", []),
        "description": persona.get("description", ""),
        "confidence_score": 0.89
    }

@router.post("/task/reply")
async def task_reply(request: Request, payload: ReplyRequest):
    check_rate_limit(request.client.host)
    sid = verify_session_token(payload.session_id)
    persona = get_session(sid)
    if not persona:
        raise HTTPException(404, "Session not found. Please rebuild your twin.")
    return run_twin_workflow(persona, "reply", sanitize_input(payload.original_message))

@router.post("/task/decision")
async def task_decision(request: Request, payload: DecisionRequest):
    check_rate_limit(request.client.host)
    sid = verify_session_token(payload.session_id)
    persona = get_session(sid)
    if not persona:
        raise HTTPException(404, "Session not found.")
    opts = sanitize_list(payload.options)
    full = f"Situation: {sanitize_input(payload.situation)}\nOptions:\n" + "\n".join(f"- {o}" for o in opts)
    return run_twin_workflow(persona, "decision", full)

@router.post("/task/plan")
async def task_plan(request: Request, payload: PlanRequest):
    check_rate_limit(request.client.host)
    sid = verify_session_token(payload.session_id)
    persona = get_session(sid)
    if not persona:
        raise HTTPException(404, "Session not found.")
    full = f"Goal: {sanitize_input(payload.goal)}\nTimeframe: {payload.timeframe}"
    return run_twin_workflow(persona, "plan", full)

@router.delete("/session")
async def clear_session(session_token: str):
    try:
        sid = verify_session_token(session_token)
        _sessions.pop(sid, None)
    except:
        pass
    return {"message": "Session cleared."}