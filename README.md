
# **VisitFlow**

VisitFlow is a lightweight, human‑centered workflow system designed to support intentional job‑search habits, reduce cognitive load, and bring structure to a process that is often chaotic, emotional, and asymmetric.

It is not a CRM.  
It is not an automation engine.  
It is not a job‑application tracker.

VisitFlow is a **personal companion** that helps you stay focused, disciplined, and emotionally steady while navigating the modern job market.

---

# **Table of Contents**

- [Purpose](#purpose)  
- [Philosophy](#philosophy)  
- [MVP 1.0 Features](#mvp-10-features)  
- [Architecture Overview](#architecture-overview)  
- [Running VisitFlow](#running-visitflow)  
- [Data Storage](#data-storage)  
- [Security Notes](#security-notes)  
- [Roadmap](#roadmap)  
- [License](#license)

---

# **Purpose**

VisitFlow exists to:

- help you stay intentional during your job search  
- reduce cognitive load  
- provide predictable reminders  
- capture structured reflections  
- support emotional stability  
- keep important threads visible  
- avoid overwhelm  

It is designed for **human speed**, not machine speed.

---

# **Philosophy**

VisitFlow is built around a few core principles:

### **1. Human‑centered workflow**
The system supports focus, reflection, and emotional stability — not volume or automation.

### **2. Cognitive unloading**
Your mind stays clear.  
The system holds the details.

### **3. Clarity over complexity**
Minimal dependencies.  
Predictable behavior.  
No hidden state.

### **4. Replaceable components**
Storage, pipeline, and UI can evolve independently.

### **5. Extensibility without architectural debt**
The system is small but structured like a real product.

---

# **MVP 1.0 Features**

### ✔ **Company Tracking**
- Add companies you want to intentionally follow  
- Assign value (high/medium/low)  
- Set reminder frequency (daily/weekly/monthly/specific date/none)  
- Track last visited and last applied timestamps  

### ✔ **Visit Pipeline**
Each visit runs through a lightweight NLP pipeline:
- normalization  
- structure extraction  
- insights  
- sentiment/energy detection  
- narrative generation  
- recommended next steps  

### ✔ **Timeline**
A chronological view of all visits with:
- timestamps  
- sentiment  
- energy  
- key points  
- preview of notes  

### ✔ **FreeNotes**
A simple, timestamped space for:
- brain dumps  
- reflections  
- ideas  
- daily notes  

### ✔ **Dashboard**
Shows:
- overdue companies  
- due today  
- upcoming  
- never checked  
- no due date  

### ✔ **JSON Durability**
All data is stored locally in:
```
data/companies.json
data/visits.json
data/freenotes.json
```

---

# **Architecture Overview**

VisitFlow uses a clean, layered architecture:

```
main.py
  ↓
routes_api.py      routes_pages.py
  ↓                     ↓
store.py            store.py
  ↓                     ↓
JSON files         templates/
```

### **Layers**

#### **API Layer (`routes_api.py`)**
- JSON endpoints  
- No templates  
- Programmatic access (CLI, agents, scripts)

#### **UI Layer (`routes_pages.py`)**
- HTML templates  
- Human‑friendly views  
- Dashboard, companies, timeline, freenotes

#### **Store Layer (`store.py`)**
- Single source of truth  
- Load/save JSON  
- Business logic  
- ID generation  

#### **Pipeline Layer (`pipeline.py`)**
- Stateless NLP transformations  
- Replaceable in future versions  

For full details, see **Architecture.md** and **DeveloperGuide.md**.

---

# **Running VisitFlow**

### **1. Install dependencies**
```
pip install -r requirements.txt
```

### **2. Start the server**
```
uvicorn main:app --reload
```

### **3. Open in browser**
Visit:
```
http://127.0.0.1:8000
```

---

# **Data Storage**

VisitFlow uses simple JSON files for MVP 1.0:

```
data/
  companies.json
  visits.json
  freenotes.json
```

### Why JSON?
- portable  
- easy to inspect  
- easy to debug  
- zero dependencies  
- ideal for local‑only MVP  

Future versions will support SQLite for indexing, search, and pagination.

---

# **Security Notes**

VisitFlow MVP 1.0 is designed for **local‑only** use.

- No authentication  
- No external network calls  
- No cloud storage  
- No third‑party APIs  
- No sensitive data collected  

Before making the repository public, the following were reviewed:

- No secrets or credentials in code  
- No personal data in JSON files  
- `.gitignore` configured  
- Apache 2.0 license added  
- GitHub security features can be enabled (optional)

VisitFlow runs only on `127.0.0.1` in MVP 1.0.  
This local‑only boundary *is* the security model, and authentication is intentionally deferred.

Because the server is not exposed to the network, the attack surface is effectively eliminated.  
Authentication will be introduced only when VisitFlow supports remote access, multi‑device sync, or shared environments.

---

# **Roadmap**

### **MVP 2.0**
- Edit/delete FreeNotes  
- Edit company details  
- Pagination for companies and timeline  
- Reload config button  
- Sorting improvements (soonest/oldest)  
- UI polish  
- Drift cleanup between API and UI  
- Error handling standardization  

### **MVP 3.0**
- SQLite migration  
- Tagging and NLP search  
- Analytics and insights  
- Browser extension  
- Background agents (job‑site scanning)  
- Authentication (local or Windows)  

### **Long‑term**
- Local SLM integration  
- Export/import  
- Multi‑device sync  
- Plugin system  

---

# **License**

VisitFlow is licensed under the **Apache License 2.0**.  
See the `LICENSE` file for details.


---
