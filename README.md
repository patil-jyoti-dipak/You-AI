# You² AI — Your Digital Twin

> **"Your Mind, Multiplied Safely."**  
> An agentic AI system that learns how you think, communicate, and decide — then replicates it safely.

---
---

## What is You² AI?

You² AI is a **multi-agent AI system** that builds a digital representation of a user's thinking and communication style. Unlike generic AI assistants, it:

- Learns **how you specifically** write and communicate
- Simulates **how you would decide** between options
- Provides **transparent reasoning** for every output
- Includes a **dedicated Safety Agent** to prevent misuse

---

##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    You² AI Pipeline                      │
│                                                          │
│  User Input                                              │
│      │                                                   │
│      ▼                                                   │
│  ┌──────────────┐                                        │
│  │ Persona Agent│ ← Extracts personality profile         │
│  └──────┬───────┘                                        │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────┐                                    │
│  │ Decision/Response│ ← Generates personalized output    │
│  │      Agent       │                                    │
│  └──────┬───────────┘                                    │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                        │
│  │ Critic Agent │ ← Validates personality consistency    │
│  └──────┬───────┘                                        │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                        │
│  │ Safety Agent │ ← Blocks harmful/unethical outputs     │
│  └──────┬───────┘                                        │
│         │                                                │
│         ▼                                                │
│  ┌────────────────┐                                      │
│  │Explainer Agent │ ← Generates transparent reasoning    │
│  └──────┬─────────┘                                      │
│         │                                                │
│         ▼                                                │
│  Final Output (Content + Reasoning + Confidence)         │
└─────────────────────────────────────────────────────────┘
```

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI/LLM** | OpenAI GPT-4o-mini / GPT-4o |
| **Agent Orchestration** | Custom async pipeline (Python) |
| **Backend** | FastAPI + Uvicorn |
| **Rate Limiting** | SlowAPI |
| **Input Validation** | Pydantic v2 |
| **Frontend** | React 18 + Vite |
| **Styling** | TailwindCSS |
| **Fonts** | Bebas Neue, Outfit, JetBrains Mono |

---

##  Project Structure

```
you2ai/
├── backend/
│   ├── main.py            # FastAPI app + all routes
│   ├── agents.py          # 5-agent multi-agent pipeline
│   ├── models.py          # Pydantic data models
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment config template
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── LandingPage.jsx       # Hero + features
    │   │   ├── PersonaSetupPage.jsx  # 3-step setup wizard
    │   │   ├── DashboardPage.jsx     # Main interaction hub
    │   │   └── SafetyPage.jsx        # Ethics & safety
    │   ├── components/
    │   │   └── Navbar.jsx
    │   ├── services/
    │   │   └── api.js                # Axios API service
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css                 # Custom design system
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    └── package.json
```

---



### 3. Use the App

1. Open `http://localhost:5173`
2. Click **"Build Your Twin"**
3. Upload 5–15 of your own messages
4. Set your preferences (tone, decision style, communication style)
5. Click **"Analyze & Build Twin"**
6. Go to **Dashboard** and try:
   - **Communicate** — paste a message to respond to
   - **Decide** — describe a situation with 2+ options

---

## Security Features

| Feature | Implementation |
|---------|---------------|
| Rate Limiting | 10–20 req/min per IP via SlowAPI |
| Input Sanitization | Pydantic validators + text sanitization |
| Security Headers | X-Content-Type-Options, X-Frame-Options, XSS-Protection |
| CORS | Strict origin whitelist |
| Session Expiry | 1-hour TTL with GDPR-compliant deletion |
| Safety Layer | Dual: LLM Safety Agent + hard-coded pattern blocks |
| No Persistent DB | In-memory session store (no data at rest) |

---

## The 5 Agents Explained

### 1. Persona Agent
Analyzes text samples using structured prompting to extract:
- Tone (formal/casual/mixed)
- Decision style (risky/balanced/safe)
- Vocabulary level, dominant emotion
- Linguistic patterns and decision anchors

### 2. Decision/Response Agent
Core reasoning engine. Uses the persona profile to generate outputs exactly as the user would write them. Separate prompts for communication vs decision tasks.

### 3. Critic Agent
Independently evaluates whether the output truly matches the personality profile. If consistency score drops below threshold, it refines the output before proceeding.

### 4. Safety Agent
Two-tier validation:
- **LLM-based**: Nuanced evaluation of manipulation, harm, impersonation
- **Hard-coded**: Pattern matching for zero-tolerance categories (violence, illegal content, etc.)

### 5. Explainer Agent
Generates human-readable reasoning explaining which personality traits influenced each decision, making the system transparent and trustworthy.

---

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/persona/analyze` | Build personality profile |
| `POST` | `/api/twin/communicate` | Generate personalized reply |
| `POST` | `/api/twin/decide` | Simulate user decision |
| `GET` | `/api/session/{id}/persona` | Retrieve session persona |
| `DELETE` | `/api/session/{id}` | GDPR session deletion |
| `GET` | `/api/docs` | Swagger UI (dev only) |

---

## 🏆 What Makes This Different

| Feature | Other AI Twins | You² AI |
|---------|---------------|---------|
| Style mimic | ✅ | ✅ |
| Tone matching | ✅ | ✅ |
| Decision simulation | ❌ | ✅ |
| Multi-agent reasoning | ❌ | ✅ (5 agents) |
| Safety layer | Weak | Dual-layer hard safety |
| Explainable outputs | ❌ | ✅ Full reasoning |
| GDPR-compliant | ❌ | ✅ Session deletion |

---

## 🚀 Future Roadmap

- [ ] Real-time persona learning (adapts over time)
- [ ] Compare Mode: "You vs Best Version of You"
- [ ] Multi-language personality profiles
- [ ] Integration with Gmail / calendar APIs
- [ ] Export twin profile as portable JSON
- [ ] Enterprise: HR decision-support, training systems

---

##  Ethical Commitment

You² AI was designed with safety as a first-class feature:

1. **Consent first** — Users explicitly provide their own data
2. **Identity lock** — Cannot impersonate real people
3. **Suggestions only** — Never takes autonomous real-world actions
4. **Full transparency** — Every output includes reasoning
5. **Minimum data** — We collect only what's necessary

---



---

*Built for International Hackathon · Safe by Design · Your Mind, Multiplied.*

