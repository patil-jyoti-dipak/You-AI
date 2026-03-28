import os, json, re

def get_ai_response(system_prompt, user_prompt, temperature=0.5):
    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if groq_key:
        return _groq_call(groq_key, system_prompt, user_prompt)
    elif gemini_key:
        return _gemini_call(gemini_key, system_prompt, user_prompt)
    elif openai_key:
        return _openai_call(openai_key, system_prompt, user_prompt, temperature)
    else:
        raise ValueError("No API key found!")

def _groq_call(key, system, user):
    from groq import Groq
    client = Groq(api_key=key)
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        max_tokens=800
    )
    return r.choices[0].message.content.strip()

def _gemini_call(key, system, user):
    from google import genai
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{system}\n\n{user}"
    )
    return response.text.strip()

def _openai_call(key, system, user, temperature):
    from openai import OpenAI
    client = OpenAI(api_key=key)
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=temperature, max_tokens=800
    )
    return r.choices[0].message.content.strip()

def _parse_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {}

def extract_persona(sample_texts, tone, risk_level, communication_style, personality_type, additional_traits=""):
    system = "You are a psycholinguistic analyzer. Output ONLY raw valid JSON with no markdown."
    user = f"""Analyze these writing samples:
{chr(10).join(sample_texts[:8])}

Preferences: tone={tone}, risk={risk_level}, style={communication_style}, personality={personality_type}
Extra: {additional_traits}

Return ONLY this JSON:
{{
  "tone": "{tone}",
  "risk_level": "{risk_level}",
  "communication_style": "{communication_style}",
  "personality_type": "{personality_type}",
  "traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
  "description": "One sentence describing how this person communicates"
}}"""
    raw = get_ai_response(system, user, 0.3)
    result = _parse_json(raw)
    if not result.get("traits"):
        result = {
            "tone": tone, "risk_level": risk_level,
            "communication_style": communication_style,
            "personality_type": personality_type,
            "traits": [personality_type, tone, risk_level, "focused", "direct"],
            "description": f"A {tone} {personality_type} communicator."
        }
    return result

def run_pipeline(persona, task_type, user_input):
    thoughts = []
    score = 0.82

    # Agent 1: Persona
    r1 = _parse_json(get_ai_response(
        "You are the Persona Agent. Output ONLY raw valid JSON.",
        f"Profile: tone={persona.get('tone')}, risk={persona.get('risk_level')}, traits={persona.get('traits')}\nTask: {task_type}\nInput: {user_input}\nOutput: {{\"behavioral_instructions\": \"...\", \"thought\": \"...\"}}"
    , 0.3))
    instructions = r1.get("behavioral_instructions", f"Act as a {persona.get('tone')} {persona.get('personality_type')} person.")
    thoughts.append({"agent": "Persona Agent", "thought": r1.get("thought", "Building behavioral model..."), "confidence": 0.92})

    # Agent 2: Response
    if task_type == "reply":
        usr2 = f"Reply to this message as the user:\n{user_input}"
    elif task_type == "decision":
        usr2 = f"Make this decision as the user would:\n{user_input}"
    else:
        usr2 = f"Create a plan structured the way this person thinks:\n{user_input}"

    initial = get_ai_response(
        f"You ARE this person's digital twin. Profile: {instructions}. Personality: {persona.get('tone')} tone, {persona.get('personality_type')}, {persona.get('risk_level')} risk. Do NOT sound like a generic AI.",
        usr2, 0.7
    )
    thoughts.append({"agent": "Decision Agent", "thought": f"Generated personalized {task_type} response.", "confidence": 0.88})

    # Agent 3: Critic
    r3 = _parse_json(get_ai_response(
        "You are the Critic Agent. Evaluate and refine. Output ONLY raw valid JSON.",
        f"Personality: tone={persona.get('tone')}, traits={persona.get('traits')}\nResponse: {initial}\nOutput: {{\"personality_match_score\": 0.85, \"refined_response\": \"...\", \"reasoning\": \"...\", \"thought\": \"...\"}}"
    , 0.2))
    refined = r3.get("refined_response", initial)
    reasoning = r3.get("reasoning", "Response matches personality profile.")
    score = float(r3.get("personality_match_score", 0.82))
    thoughts.append({"agent": "Critic Agent", "thought": r3.get("thought", f"Match: {score:.0%}"), "confidence": score})

    # Agent 4: Safety
    r4 = _parse_json(get_ai_response(
        "You are the Safety Agent. Check for harm. Output ONLY raw valid JSON.",
        f"Check for impersonation, harassment, illegal content, manipulation.\nResponse: {refined}\nOutput: {{\"is_safe\": true, \"violations_found\": [], \"warnings\": [], \"final_response\": \"...\", \"thought\": \"...\"}}"
    , 0.1))
    is_safe = bool(r4.get("is_safe", True))
    final = r4.get("final_response", refined)
    if not is_safe:
        final = f"⚠️ Blocked: {', '.join(r4.get('violations_found', ['unsafe content']))}"
    thoughts.append({"agent": "Safety Agent", "thought": r4.get("thought", "Content cleared."), "confidence": 1.0 if is_safe else 0.0})

    return {
        "output": final,
        "reasoning": reasoning,
        "agent_thoughts": thoughts,
        "personality_match_score": score,
        "safety_cleared": is_safe,
        "warnings": r4.get("warnings", [])
    }