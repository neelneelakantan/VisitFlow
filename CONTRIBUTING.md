

# Contributing to VisitFlow

Thank you for your interest in contributing to VisitFlow.  
This project is intentionally simple, human‑centered, and architected with clean seams.  
Contributions are welcome as long as they align with the project’s philosophy and design principles.

---

# **1. Project Philosophy**

VisitFlow is built to support:

- intentional job‑search habits  
- cognitive unloading  
- emotional stability  
- human‑speed workflows  
- clarity over complexity  

Contributions should preserve these values.

This is not a CRM, not an automation engine, and not a job‑application tracker.  
Features that add noise, overwhelm, or unnecessary complexity will not be accepted.

---

# **2. How to Contribute**

### **Step 1 — Fork the repository**
Create your own fork on GitHub.

### **Step 2 — Create a feature branch**
Use a clear, descriptive name:

```
feature/edit-freenotes
fix/specific-date-bug
refactor/store-layer
```

### **Step 3 — Make your changes**
Follow the architectural guidelines:

- API routes → `routes_api.py`  
- UI routes → `routes_pages.py`  
- Persistence/business logic → `store.py`  
- NLP logic → `pipeline.py`  
- Templates → `templates/`  

Avoid mixing concerns.

### **Step 4 — Test locally**
Run the app:

```
uvicorn main:app --reload
```

Verify:

- companies load/save correctly  
- visits persist  
- freenotes persist  
- dashboard and timeline render  
- no drift between API and UI  

### **Step 5 — Submit a pull request**
Include:

- a clear description of the change  
- rationale for the change  
- screenshots if UI is affected  
- notes on backward compatibility  

---

# **3. Coding Guidelines**

### **Keep it simple**
Avoid unnecessary abstractions, frameworks, or dependencies.

### **No global state**
All data should be loaded fresh from disk via `store.py`.

### **No circular imports**
Routers must not import each other.  
Store must not import routers.

### **No persistence logic in routers**
All load/save logic belongs in `store.py`.

### **Stateless pipeline**
`pipeline.py` should remain pure and replaceable.

### **Minimal UI**
Templates should be clean, readable, and low‑cognitive‑load.

---

# **4. Commit Message Style**

Use clear, senior‑level commit messages:

```
Fix: Correct specific_date comparison in compute_next_check

Refactor: Consolidate visit logic into store.mark_visited

Feature: Add edit/delete support for FreeNotes

Docs: Add design rationale and architecture overview
```

Avoid vague messages like “update” or “misc fixes”.

---

# **5. Feature Guidelines**

### **Good candidates for contribution**
- usability improvements  
- sorting, pagination, filtering  
- small UI polish  
- drift cleanup between API and UI  
- error handling improvements  
- documentation enhancements  

### **Features that require discussion first**
- database migrations  
- authentication  
- browser extensions  
- background agents  
- analytics  
- NLP search  
- major UI redesigns  

Open an issue before implementing these.

### **Features that will not be accepted**
- automated job applications  
- CRM‑style pipelines  
- high‑volume automation  
- features that increase cognitive load  
- features that conflict with the project philosophy  

---

# **6. Code of Conduct**

Be respectful, constructive, and collaborative.  
VisitFlow is a human‑centered project — contributions should reflect that spirit.

---

# **7. License**

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.

---
