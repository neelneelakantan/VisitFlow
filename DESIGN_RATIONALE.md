
# **Design Rationale**

VisitFlow is intentionally simple, human‑centered, and architected with clean seams.  
This document explains *why* the system is designed the way it is — the tradeoffs, constraints, and guiding principles that shaped MVP 1.0 and set the foundation for future evolution.

---

# **1. Purpose of VisitFlow**

VisitFlow exists to support **intentional job‑search habits**, reduce cognitive load, and provide a stable, predictable workflow during an emotionally asymmetric process.

It is not a CRM.  
It is not an automation engine.  
It is not a job‑application tracker.

Instead, it is a **human‑speed companion** that helps you:

- stay focused  
- maintain discipline  
- avoid overwhelm  
- keep important threads visible  
- reflect with clarity  

The design choices reflect this philosophy.

---

# **2. Core Design Principles**

### **1. Human‑centered workflow**
The system is built around how humans think, not how machines operate.

- predictable reminders  
- simple categories  
- clean UI  
- no cognitive overload  
- no hidden state  

### **2. Clarity over complexity**
Every feature must reduce friction, not add it.

- no deep AI integration in MVP  
- no multi‑user complexity  
- no heavy dashboards  
- no unnecessary abstractions  

### **3. Replaceable components**
Every layer is intentionally modular:

- JSON storage → SQLite → Postgres  
- NLP pipeline → LLM → local SLM  
- UI templates → React → mobile app  

Nothing is tightly coupled.

### **4. Extensibility without architectural debt**
The system is small but structured like a real product:

- clean routing  
- separation of API and UI  
- single source of truth in `store.py`  
- stateless pipeline  
- predictable data flow  

This allows future growth without rewrites.

### **5. Emotional safety**
The system avoids:

- noisy alerts  
- overwhelming dashboards  
- guilt‑inducing metrics  
- automation that removes agency  

VisitFlow is designed to feel calm, supportive, and human.

---

# **3. Why JSON for MVP 1.0**

### **Reasons for choosing JSON:**

- zero dependencies  
- portable  
- easy to inspect  
- easy to debug  
- ideal for local‑only workflows  
- perfect for a personal tool  
- avoids premature complexity  

### **Tradeoff**
JSON is not ideal for:

- pagination  
- indexing  
- search  
- concurrency  

These are intentionally deferred to MVP 2.0+.

---

# **4. Why No Authentication in MVP 1.0**

VisitFlow is designed for **local‑only** use in MVP 1.0.

Adding authentication would:

- increase friction  
- add boilerplate  
- require session management  
- complicate the UI  
- distract from core workflow goals  

### **Tradeoff**
Authentication is planned for future versions when:

- remote hosting  
- multi‑device access  
- shared environments  

become relevant.

---

## Why VisitFlow Does Not Include Login or Authentication in MVP 1.0

VisitFlow is intentionally designed as a **local‑only** application in MVP 1.0.  
The server binds to `127.0.0.1` and is not exposed to the network.  
This eliminates the external attack surface and makes authentication unnecessary.

Adding login at this stage would:

- increase friction  
- introduce UI and session‑management complexity  
- require password storage or OS‑level integration  
- distract from the core workflow goals  
- create more cognitive load for the user  

Authentication will be introduced only when VisitFlow supports:

- remote hosting  
- multi‑device access  
- shared environments  
- cloud or network‑accessible deployments  

Until then, **local‑only execution is the security boundary**.

# **5. Why No Application Tracking**

This is a deliberate choice.

Most job‑application trackers:

- create noise  
- encourage volume over intention  
- flood the user with low‑value data  
- duplicate what email already handles well  

VisitFlow focuses on:

- reminders  
- structured visits  
- insights  
- cognitive unloading  

Application tracking is intentionally excluded to preserve clarity.

---

# **6. Why Visits Use a Pipeline**

The visit pipeline is intentionally simple:

1. ingest  
2. normalize  
3. extract structure  
4. generate insights  
5. generate narrative  
6. recommend next steps  

### **Reasons for this design:**

- predictable  
- explainable  
- easy to test  
- easy to replace with LLMs later  
- supports human reflection  
- avoids black‑box behavior  

The pipeline is a **replaceable connector**, not a monolith.

---

# **7. Why FreeNotes Are Append‑Only in MVP**

FreeNotes behave like an event log in MVP 1.0.

### **Reasons:**

- simplest durable model  
- avoids UI complexity  
- avoids versioning  
- avoids edit/delete semantics  
- keeps MVP focused  

### **Tradeoff**
Editing FreeNotes is important for real workflows and will be added in MVP 2.0.

---

# **8. Why API and UI Are Separate**

This is a foundational architectural decision.

### **Benefits:**

- prevents circular imports  
- keeps UI clean  
- keeps API testable  
- supports future CLI/mobile/agent integrations  
- avoids drift between JSON and HTML responses  
- enforces separation of concerns  

### **Tradeoff**
Some boilerplate is duplicated in MVP 1.0.  
This is acceptable and will be consolidated in MVP 2.0.

---

# **9. Why No Global State**

VisitFlow loads fresh data from disk on each request.

### **Reasons:**

- avoids stale state  
- avoids race conditions  
- avoids hidden bugs  
- ensures predictable behavior  
- simplifies debugging  

This is especially important for a personal tool that may be restarted frequently.

---

# **10. Why the UI Is Minimal**

The UI is intentionally:

- clean  
- text‑first  
- low‑cognitive‑load  
- predictable  
- frictionless  

### **Reasons:**

- supports emotional stability  
- avoids distraction  
- keeps the system human‑speed  
- reduces design overhead  
- aligns with the philosophy of intentionality  

Future versions may add polish, but simplicity is a feature, not a limitation.

---

# **11. Why Apache 2.0 License**

Apache 2.0 was chosen because:

- it is permissive  
- it includes explicit patent protection  
- it is enterprise‑friendly  
- it supports future productization  
- it encourages community contributions  

MIT is simpler, but Apache 2.0 is more future‑proof.

---

# **12. Summary of Key Tradeoffs**

| Decision | Reason | Deferred Complexity |
|---------|--------|---------------------|
| JSON storage | simplicity, portability | SQLite/Postgres |
| No auth | local‑only MVP | session mgmt, security |
| No application tracking | avoid noise | optional plugin |
| Append‑only FreeNotes | simplest model | edit/delete |
| Minimal UI | cognitive safety | polish, components |
| Separate API/UI | clean architecture | boilerplate cleanup |
| Lightweight pipeline | explainable | LLM integration |

These tradeoffs keep MVP 1.0 **focused, stable, and intentional**.

---

# **Conclusion**

VisitFlow is designed to feel human, not mechanical.  
Every architectural choice reflects that philosophy.

The system is:

- simple  
- predictable  
- emotionally safe  
- extensible  
- future‑proof  

This design rationale ensures that VisitFlow can evolve into a more powerful workflow engine without losing its core identity:  
**a tool that supports human focus, clarity, and intentionality.**

---
