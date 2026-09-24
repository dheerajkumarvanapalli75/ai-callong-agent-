# Master Specification: Configurable AI Phone Agent Platform

## 1. TECH STACK

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript, Vite, Tailwind, React Flow (workflow builder), TanStack Query |
| Backend | Python 3.11+, FastAPI, Pydantic v2, async throughout |
| Database | MongoDB Atlas, using the async driver Motor (or Beanie ODM) |
| Vector search | MongoDB Atlas Vector Search on `knowledge_chunks` (with a local fallback for dev, such as mongodb-atlas-local Docker or a pluggable retriever interface) |
| Auth | Own JWT auth in FastAPI (access + refresh tokens, argon2 password hashing, RBAC), with optional OAuth later |
| Voice | Vapi or Retell, behind a `VoiceProvider` interface. Twilio is used for numbers and SMS. |
| LLM | Provider-agnostic `LLMProvider` interface (Anthropic, OpenAI, others), configured per business |
| Embeddings | Pluggable `EmbeddingProvider`; store the model name and dimension with each chunk |
| Jobs | Background queue (Celery/RQ/ARQ + Redis) for document ingestion, follow-ups, and summaries |
| Realtime | WebSockets or SSE for the Test Lab and live call monitoring |
| Deploy | Docker Compose for dev, environment-based config, and a `.env.example` |

---

## 2. ARCHITECTURE RULES

1. **Structured configuration, not one giant prompt.** Each config section (identity, goal, tasks, rules, examples, objections, permissions, handoff, lead rules, languages) is stored and versioned separately. At runtime, a Prompt Compiler assembles only the relevant slices for the current turn.
2. **Deterministic orchestration around the LLM.** The pipeline for each turn is:
   `transcript → language detect → intent classify → retrieve knowledge → rule evaluation → task selection (by priority) → permission check → LLM response generation → action execution → verified result → persist`
   Rules, permissions, priorities, and handoff triggers are enforced in code, not merely requested in a prompt.
3. **Immutable published versions.** A call always runs against a single frozen `agent_versions` snapshot, never against the live draft.
4. **Voice-provider isolation.** Business logic lives in our backend. Vapi/Retell is used as a custom-LLM or webhook layer for STT, TTS, telephony, and interruption handling.
5. **Multi-tenant by design.** Every document carries `business_id`. Every query is scoped by it through a mandatory repository layer. Cross-tenant access must be impossible.
6. **Clean layering:** `api/` → `services/` → `repositories/` → `models/`, plus `runtime/` (the call engine), `integrations/`, and `providers/`.

---

## 3. MONGODB DATA MODEL

Use one collection per entity. Reference by ObjectId. Embed only small, tightly-coupled data. Add `created_at`, `updated_at`, and `business_id` to every document.

**Collections (26):**
- `users`
- `businesses`
- `agents`
- `agent_versions`
- `agent_tasks`
- `agent_rules`
- `agent_examples`
- `agent_objections`
- `agent_permissions`
- `agent_intents`
- `agent_lead_rules`
- `agent_handoff_rules`
- `agent_workflows`
- `languages`
- `knowledge_documents`
- `knowledge_chunks`
- `customers`
- `calls`
- `conversation_messages`
- `call_summaries`
- `leads`
- `follow_ups`
- `registrations`
- `agent_actions`
- `test_scenarios`
- `test_runs`
- `integrations`
- `audit_logs`
- `consent_records`

### Key Design Decisions
- `agent_versions` stores a full config snapshot (embedded tasks, rules, examples, etc.), a `knowledge_version` reference, a semantic version (`v1.2`), `created_by`, a `change_summary`, and a status (`draft` | `published` | `archived`).
- `knowledge_chunks` holds text, embedding (vector), `document_id`, `category`, `language`, `embedding_model`, and `doc_version`. It gets an Atlas Vector Search index with a filter on `business_id` and `category`.
- `conversation_messages` holds `call_id`, `customer_id`, `role`, `text`, `language`, `timestamp`, and `metadata` (intent, task, retrieved chunk IDs, confidence). It is indexed on `(business_id, call_id, timestamp)`.
- `customers` has a unique `customer_id`, normalized E.164 phone numbers, and a unique compound index on `(business_id, phone)`. All memory retrieval is keyed on `customer_id` and `business_id`.
- `agent_actions` is an audit trail of every tool invocation: request, permission decision, provider response, and `confirmed: true/false`.

### Agent Configuration Object (Stored in Version Snapshot)
```json
{
  "identity": {"name": "", "role": "", "business_name": "", "personality": [], "speaking_style": []},
  "goal": "",
  "languages": [{"code": "", "voice": "", "greeting": "", "terminology": [], "style": ""}],
  "tasks": [],
  "rules": [],
  "examples": [],
  "objections": [],
  "intents": [],
  "lead_rules": [],
  "permissions": [],
  "handoff_rules": [],
  "workflow": {},
  "llm": {"provider": "", "model": "", "temperature": 0.3},
  "knowledge_version": ""
}
```

---

## 4. AGENT TRAINING CENTER (16 Modules)

1. **Agent Identity:** name, role, business, personality (multi-select), speaking style.
2. **Agent Goal:** main objective statement.
3. **Tasks:** Task Builder with trigger, required fields, ordered steps, allowed tools, priority (HIGH/MEDIUM/LOW), enabled flag. Starter templates provided.
4. **Business Knowledge:** Knowledge Base with text, PDF, DOCX, FAQ pairs, URL crawler, category assignment, semantic chunking (~300-500 tokens), embeddings, approved flag.
5. **Conversation Rules:** Global behavioral constraints and guidelines.
6. **Customer Handling:** Returning vs new caller behavior.
7. **Objection Handling:** Objection library with variants, verified guidance, and actions.
8. **Lead Qualification:** Classification evidence rules for statuses (`INTERESTED`, `NOT_INTERESTED`, `FOLLOW_UP_REQUIRED`, `UNCERTAIN`, `REGISTERED`, `ALREADY_REGISTERED`).
9. **Allowed Actions & 10. Restricted Actions:** Combined Permissions Matrix (`ALLOW` / `DENY` / `CONFIRM_BEFORE_ACTION`).
11. **Languages:** Per-language voice, greetings, glossary, styles (English, Telugu, Hindi, etc.).
12. **Example Conversations:** Teach by example dialog pairs.
13. **Call Flow:** React Flow visual graph builder (Start, Speak, Listen, Search Knowledge, Call Tool, Condition, Transfer, End).
14. **Human Handoff:** Trigger rules, operator briefing, callback fallback.
15. **Test Agent:** Testing Lab with live simulation.
16. **Version History:** View, diff, restore-as-new-version.

---

## 5. RUNTIME BEHAVIOR
- **Accuracy over guessing:** Grounded strictly in approved knowledge. Below threshold => "I don't have verified information about that. I can connect you with our team to confirm."
- **Grounding trace:** Every factual reply includes cited chunk IDs.
- **Permission enforcement in code:** `DENY` is strictly blocked in tool executor. `CONFIRM` requires explicit transcript confirmation.
- **Completion honesty:** Replies may only claim an action succeeded if `confirmed: true`.
- **Customer isolation:** Scoped strictly by `(business_id, customer_id)`.
- **Latency target:** < 1.2s to first token with streaming.

---

## 6. ACTIONS & TOOLS
Pluggable tools with schemas, timeouts, retries, idempotency keys, and audit logging:
`search_knowledge`, `create_update_customer`, `save_conversation`, `update_lead_status`, `send_registration_link`, `schedule_follow_up`, `check_registration_status`, `transfer_call`, `send_sms`, `send_whatsapp`, `send_email`.

---

## 7. TESTING LAB & EVALUATION
- Test chat showing intent, task, knowledge chunks, simulated actions, lead status, confidence.
- Predefined scenarios with assertions (including discount probe, prompt injection, multilingual).
- Scenario runner with `PASSED` / `FAILED` / `NEEDS REVIEW`.
- Regression deployment gating.

---

## 8. DEPLOYMENT WORKFLOW
- Pipeline: `DRAFT` → `TRAINING` → `TESTING` → `READY` → `DEPLOYED`.
- Automated checklist verification.
- Immutable frozen snapshot with 1-click rollback.

---

## 9. CALLS, HISTORY & ANALYTICS
- Per-call metadata, timeline, summary, and recording references.
- Analytics: volume, handoff rates, funnel, unknown-question gap list.

---

## 10. COMPLIANCE & SECURITY
- Consent records, calling hours, do-not-call lists, TCPA/TRAI awareness.
- RBAC (`owner`, `admin`, `agent-operator`, `viewer`), argon2 password hashing, JWT access/refresh tokens.
- Secret encryption at rest, webhook signature verification, PII redaction.
