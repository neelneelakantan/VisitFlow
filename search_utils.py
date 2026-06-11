# search_utils.py

import urllib.parse

def safe_url(url: str) -> str:
    return urllib.parse.quote(url, safe=":/?=&%")


def search_entities(q: str, company_store, harvester_list):
    q_lower = q.lower()

    def match_company(c):
        return (
            q_lower in c.name.lower()
            or any(q_lower in u.lower() for u in c.urls)
            or q_lower in (c.notes or "").lower()
            or q_lower in c.value.lower()
        )

    def match_harvester(h):
        return (
            q_lower in h["name"].lower()
            or q_lower in (h.get("source_url") or "").lower()
            or q_lower in (h.get("careers_url") or "").lower()
        )

    companies = [c for c in company_store.list_companies() if match_company(c)]
    harvested = [h for h in harvester_list if match_harvester(h)]

    return companies, harvested

