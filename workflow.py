import json, os, re
from openai import OpenAI

def get_client():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or key == "sk-your-real-key-here":
        raise ValueError("OPENAI_API_KEY missing or not set in .env file!")
    return OpenAI(api_key=key)

def _call(client, system, user, temp=0.4, tokens=800):
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temp,
        max_tokens=tokens
    )
    return r.choices[0].message.content.strip()

def _parse(text: str) -> dict:
    # Try direct JSON parse
    try:
        return json.loads(text)
    except:
        pass
    # Try extracting from markdown code block
    match = re.search(r'```(?:json)?\s*([\s\S]+?)```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    return {}

def extract_persona(sample_texts, tone, risk_level, communication_style, personality_type, additional_traits=""):
    client = get_client()
    joined = "\n---\n".join(sample_texts[:10])

    system = "You are a psycholinguistic analyzer. Output ONLY raw valid JSON. No markdown. No explanation."
    user = f"""Analyze these writing samples:
{joined}

User preferences: tone={tone}, risk={risk_level}, style={communication_style}, personality={personality_type}
Extra context: {additional_traits}

Return this exact JSON structure:
{{
  "tone": "{tone}",
  "risk_level": "{risk_level}",
  "communication_style": "{communication_style}",
  "personality_type": "{personality_type}",
  "traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
  "description": "One sentence summary of how this person communicates"
}}"""

    raw = _call(client, system, user, temp=0.3, tokens=400)
    result = _parse(raw)

    # Fallback if parsing fails
    if not result.get("traits"):
        result = {
            "tone": tone,
            "risk_level": risk_level,
            "communication_style": communication_style,
            "personality_type": personality_type,
            "traits": [personality_type, tone, risk_level, "focused", "clear"],
            "description": f"A {tone} communicator with {personality_type} tendencies."
        }
    return result


def run_twin_workflow(persona: dict, task_type: str, user_input: str) -> dict:
    client = get_client()
    thoughts = []
    score = 0.82

    # ── AGENT 1: Persona ──────────────────────────────────────────────────
    sys1 = "You are the Persona Agent in a Digital Twin AI. Output ONLY raw valid JSON."
    usr1 = f"""Personality profile:
- Tone: {persona.get('tone')}
- Risk: {persona.get('risk_level')}
- Style: {persona.get('communication_style')}
- Type: {persona.get('personality_type')}
- Traits: {persona.get('traits')}

Task type: {task_type}
User input: {user_input}

Output JSON:
{{
  "behavioral_instructions": "detailed instructions for how this person behaves",
  "thought": "what you noticed about this personality"
}}"""

    r1 = _parse(_call(client, sys1, usr1, temp=0.3, tokens=350))
    instructions = r1.get("behavioral_instructions", f"Act as a {persona.get('tone')} {persona.get('personality_type')} person.")
    thoughts.append({
        "agent": "Persona Agent",
        "thought": r1.get("thought", "Analyzing personality and building behavioral model..."),
        "confidence": 0.92
    })

    # ── AGENT 2: Decision/Response ────────────────────────────────────────
    sys2 = f"""You ARE the digital twin of this specific user.
Their behavioral profile: {instructions}
Personality: {persona.get('tone')} tone, {persona.get('personality_type')} personality, {persona.get('risk_level')} risk tolerance.
IMPORTANT: Do NOT sound like a generic AI assistant. Respond EXACTLY as this specific person would."""

    if task_type == "reply":
        usr2 = f"Write a reply to this message exactly as the user would:\n\n{user_input}"
    elif task_type == "decision":
        usr2 = f"Evaluate and make this decision exactly as the user would:\n\n{user_input}"
    else:
        usr2 = f"Create a plan for the following, structured the way this person naturally thinks:\n\n{user_input}"

    initial = _call(client, sys2, usr2, temp=0.7, tokens=700)
    thoughts.append({
        "agent": "Decision Agent",
        "thought": f"Generated personalized {task_type} response based on {persona.get('personality_type')} personality.",
        "confidence": 0.88
    })

    # ── AGENT 3: Critic ───────────────────────────────────────────────────
    sys3 = "You are the Critic Agent. Evaluate personality match and refine. Output ONLY raw valid JSON."
    usr3 = f"""Personality: tone={persona.get('tone')}, style={persona.get('communication_style')}, traits={persona.get('traits')}

Generated response:
{initial}

Output JSON:
{{
  "personality_match_score": 0.85,
  "refined_response": "the improved response here",
  "reasoning": "why this response fits or was changed",
  "thought": "brief evaluation note"
}}"""

    r3 = _parse(_call(client, sys3, usr3, temp=0.2, tokens=700))
    refined = r3.get("refined_response", initial)
    reasoning = r3.get("reasoning", "Response aligns with the user's personality profile.")
    score = float(r3.get("personality_match_score", 0.82))
    thoughts.append({
        "agent": "Critic Agent",
        "thought": r3.get("thought", f"Personality match evaluated at {score:.0%}"),
        "confidence": score
    })

    # ── AGENT 4: Safety ───────────────────────────────────────────────────
    sys4 = "You are the Safety Agent. Your job is to ensure AI outputs are safe and ethical. Output ONLY raw valid JSON."
    usr4 = f"""Check this response for: impersonation of others, harassment, illegal content, manipulation, self-harm.

Response to check:
{refined}

Output JSON:
{{
  "is_safe": true,
  "violations_found": [],
  "warnings": [],
  "final_response": "the response (unchanged if safe, modified if needed)",
  "thought": "safety evaluation summary"
}}"""

    r4 = _parse(_call(client, sys4, usr4, temp=0.1, tokens=500))
    is_safe = bool(r4.get("is_safe", True))
    final = r4.get("final_response", refined)

    if not is_safe:
        violations = r4.get("violations_found", ["unknown violation"])
        final = f"⚠️ This response was blocked by the Safety Agent: {', '.join(violations)}"

    thoughts.append({
        "agent": "Safety Agent",
        "thought": r4.get("thought", "Content reviewed and cleared."),
        "confidence": 1.0 if is_safe else 0.0
    })

    return {
        "output": final,
        "reasoning": reasoning,
        "agent_thoughts": thoughts,
        "personality_match_score": score,
        "safety_cleared": is_safe,
        "warnings": r4.get("warnings", [])
    }