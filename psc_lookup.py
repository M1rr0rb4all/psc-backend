import requests
import os

API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")
BASE_URL = "https://api.company-information.service.gov.uk"

headers = {
    "Authorization": API_KEY
}

def get_company_pscs(company_number):
    url = f"{BASE_URL}/company/{company_number}/persons-with-significant-control"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"items": []}

def search_company_number(company_name):
    url = f"{BASE_URL}/search/companies?q={company_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            if company_name.lower() in item.get("title", "").lower():
                return item.get("company_number")
    return None

def is_likely_uk_company(name):
    return name.lower().endswith((" ltd", "limited", "plc"))

def parse_pscs(data):
    pscs = []
    for item in data.get("items", []):
        if "ceased_on" in item:
            continue
        name = item.get("name") or item.get("corporate_name")
        kind = "individual" if "name" in item else "company"
        control = item.get("nature_of_control", [])
        if name:
            pscs.append({
                "name": name,
                "kind": kind,
                "nature_of_control": control,
            })
    return pscs

def build_structure(company_number, visited=None):
    if visited is None:
        visited = set()
    if company_number in visited:
        return None
    visited.add(company_number)

    data = get_company_pscs(company_number)
    pscs = parse_pscs(data)

    structure = {
        "company_number": company_number,
        "pscs": [],
    }

    for psc in pscs:
        child_node = {
            "name": psc["name"],
            "kind": psc["kind"],
            "nature_of_control": psc["nature_of_control"],
        }
        if psc["kind"] == "company" and is_likely_uk_company(psc["name"]):
            child_number = search_company_number(psc["name"])
            if child_number:
                child_node["child_pscs"] = build_structure(child_number, visited)
        structure["pscs"].append(child_node)
    return structure