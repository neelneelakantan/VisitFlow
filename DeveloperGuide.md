
# **VisitFlow Developer Guide**

This guide provides practical instructions for contributing to VisitFlow, understanding its architecture, and extending the system safely. It is intentionally concise, high‑signal, and aligned with the project’s layered design.

---

# **1. Project Philosophy**

VisitFlow is built to support intentional job‑search habits, cognitive unloading, and structured follow‑ups.  
The codebase reflects these values:

- **Clarity over cleverness**  
- **Predictability over magic**  
- **Human‑centered workflows**  
- **Small, composable modules**  
- **No hidden state**  
- **No circular imports**  
- **Easy to extend without rewrites**

This guide explains how to work within that philosophy.

---

# **2. Repository Structure**

```
visitflow/
│
├── main.py                 # FastAPI app assembly
│
├── routes_api.py           # JSON API endpoints
├── routes_pages.py         # HTML UI endpoints
│
├── store.py                # Persistence + business logic
├── pipeline.py             # NLP transformation pipeline
├── utils.py                # Shared helpers
│
├── models.py               # Pydantic models
│
├── templates/              # Jinja2 templates
├── static/                 # CSS, JS, assets
│
└── data/                   # JSON storage (MVP persistence)
```

---

# **3. Layer Responsibilities**

VisitFlow uses a clean, acyclic dependency structure.

## **3.1 API Layer (`routes_api.py`)**
- JSON endpoints only  
- No templates  
- No UI logic  
- No imports from `routes_pages`  
- Calls into `store.py` for persistence  

Examples:
- `/companies`
- `/companies/{id}`
- `/api/freenotes`
- `/visit` (pipeline)

## **3.2 UI Layer (`routes_pages.py`)**
- HTML templates only  
- No JSON endpoints  
- No imports from `routes_api`  
- Calls into `store.py` for persistence  

Examples:
- `/`
- `/companies`
- `/freenotes`
- `/freenotes/new`

## **3.3 Store Layer (`store.py`)**
- Single source of truth for persistence  
- Loads/saves JSON  
- Generates IDs  
- Contains business logic  
- No FastAPI imports  
- No router imports  

Examples:
- `load_freenotes()`
- `save_freenotes()`
- `add_freenote()`
- `list_companies()`
- `add_company()`

## **3.4 Pipeline Layer (`pipeline.py`)**
- NLP transformations  
- Stateless  
- Pure functions  

Used by:
- `/visit` API endpoint  
- UI pages that need structured visit records  

---

# **4. Adding New Routes**

## **4.1 Adding an API Route**
Add to `routes_api.py` when:

- The output is JSON  
- The route is intended for programmatic access  
- It may be used by CLI, mobile, or agents  

**Do not** render templates here.

Example:

```python
@router.get("/api/items")
def list_items():
    return store.list_items()
```

## **4.2 Adding a UI Route**
Add to `routes_pages.py` when:

- The output is HTML  
- The route renders a template  
- It is intended for human interaction  

Example:

```python
@router.get("/items")
def items_page(request: Request):
    items = store.list_items()
    return templates.TemplateResponse("items.html", {"request": request, "items": items})
```

---

# **5. Adding Persistence Logic**

All persistence and business logic belongs in `store.py`.

### **Do not:**
- Write files in routers  
- Generate IDs in routers  
- Maintain global state  
- Duplicate logic across layers  

### **Do:**
- Add a clean function in `store.py`  
- Call it from both API and UI layers  

Example:

```python
def add_item(name: str):
    items = load_items()
    new_id = max([i["id"] for i in items], default=0) + 1
    item = {"id": new_id, "name": name}
    items.append(item)
    save_items(items)
    return item
```

---

# **6. Template Development**

Templates live in `templates/` and use Jinja2.

Guidelines:
- Keep templates small and composable  
- Use `{% include %}` for shared components  
- Pass only the data needed for rendering  
- Avoid embedding business logic in templates  

---

# **7. JSON Persistence (MVP)**

VisitFlow uses JSON files for durability during MVP.

Guidelines:
- Always load fresh from disk (`load_*`)  
- Always save after mutation (`save_*`)  
- Never store global lists in routers  
- Never mutate in‑memory state  

This ensures predictable behavior even during reloads.


# 7.1 Local‑Only Execution (Security Boundary)

VisitFlow is intentionally designed to run **only on 127.0.0.1** in MVP 1.0.  
This is the security boundary: the app is not exposed to the network, so no
authentication, session management, or HTTPS is required.

A small guardrail in `main.py` enforces this behavior. If someone attempts to
start the server with a different host (for example `0.0.0.0` or a LAN IPv4
address), VisitFlow will refuse to start.

This keeps the system private, predictable, and aligned with the human‑centered
philosophy of MVP 1.0.

## Testing the Boundary

You can verify the guardrail works by trying:

```
uvicorn main:app --host=0.0.0.0 --port 8000
```

Expected behavior:

- VisitFlow prints an error and exits immediately.
- Windows or your browser may also warn you if you try to access a non‑localhost
  HTTP address, which is an additional layer of protection.

## Why This Matters

Local‑only execution ensures:

- privacy by default  
- no accidental exposure on the LAN  
- no need for login or password storage  
- no TLS or certificate management  
- no attack surface beyond the local machine  

Authentication and remote access will be introduced only in future versions
when VisitFlow supports multi‑device or networked use cases.



# **8. Adding New Features Safely**

When adding new functionality:

### **1. Start in `store.py`**
Define the persistence and business logic first.

### **2. Add API route (optional)**
Expose JSON if needed.

### **3. Add UI route (optional)**
Render templates for human interaction.

### **4. Add templates**
Keep them clean and minimal.

### **5. Test end‑to‑end**
Use both UI and API to validate behavior.

---

# **9. Avoiding Common Pitfalls**

### ❌ Do not import routers into each other  
This creates circular imports.

### ❌ Do not store global state  
Always load fresh from disk.

### ❌ Do not duplicate routes  
FastAPI silently overrides duplicates.

### ❌ Do not mix API and UI logic  
Keep layers clean.

### ❌ Do not write persistence logic in routers  
Use `store.py`.

---

# **10. Future Evolution**

The architecture is designed to evolve:

- SQLite migration  
- Full‑text search  
- Tagging and categorization  
- Authentication  
- Browser extension  
- Background agents  
- Analytics and insights  

The current layering supports all of these without rewrites.

---

# **11. Development Workflow**

A recommended workflow:

1. **Identify the feature**  
2. **Add store logic**  
3. **Add API route (if needed)**  
4. **Add UI route (if needed)**  
5. **Add templates**  
6. **Test end‑to‑end**  
7. **Commit with a clean message**  
8. **Push after a focused sprint**  

This keeps development intentional and stable.

---

# **12. Commit Message Style**

Use clear, senior‑level commit messages:

```
Refactor: Clean API/UI separation, remove stale freenotes state, eliminate circular imports

- Moved freenote creation logic to store.py
- Removed global freenotes list
- Removed duplicate /freenotes routes
- Cleaned API vs UI responsibilities
- Ensured store.py is the single source of truth
```

---

# **Conclusion**

This guide captures the core development principles behind VisitFlow.  
Follow these patterns and the system will remain clean, predictable, and easy to extend — even as it grows into a more powerful workflow engine.

