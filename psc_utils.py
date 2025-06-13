import requests

BASE_URL = "https://api.company-information.service.gov.uk"

def search_company(name, api_key):
    url = f"{BASE_URL}/search/companies?q={name}"
    response = requests.get(url, auth=(api_key, ""))
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])
    if not items:
        raise ValueError(f"No company found with name: {name}")
    return items[0]["company_number"], items[0]["title"]

def get_pscs(company_number, api_key):
    url = f"{BASE_URL}/company/{company_number}/persons-with-significant-control"
    response = requests.get(url, auth=(api_key, ""))
    response.raise_for_status()
    return response.json().get("items", [])

def is_company(name):
    name = name.lower()
    return any(name.endswith(suffix) for suffix in ["ltd", "limited"])

def build_structure(company_name, api_key, visited=None):
    if visited is None:
        visited = set()

    company_number, proper_name = search_company(company_name, api_key)

    if company_number in visited:
        return {"name": proper_name, "type": "uk-company", "children": []}

    visited.add(company_number)
    node = {
        "name": proper_name,
        "type": "uk-company",
        "children": []
    }

    pscs = get_pscs(company_number, api_key)

    for psc in pscs:
        if "ceased_on" in psc:
            continue  # Skip inactive PSCs

        nature = psc.get("nature_of_control", [])

        # Companies as PSCs
        if "name" in psc:
            name = psc["name"]
            psc_type = "uk-company" if is_company(name) else "non-uk-company"
            child = {
                "name": name,
                "type": psc_type,
                "nature_of_control": nature,
                "children": []
            }

            if is_company(name):
                try:
                    # Recursively follow PSC
                    child = build_structure(name, api_key, visited)
                    child["nature_of_control"] = nature
                except Exception:
                    pass  # Graceful fallback

            node["children"].append(child)

        # Individuals as PSCs
        elif "name_elements" in psc:
            name_parts = psc["name_elements"]
            full_name = f"{name_parts.get('forename', '')} {name_parts.get('surname', '')}".strip()
            node["children"].append({
                "name": full_name or "Individual",
                "type": "individual",
                "nature_of_control": nature,
                "children": []
            })

    return node
