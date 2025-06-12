import requests

BASE_URL = "https://api.company-information.service.gov.uk"

def search_company(company_name, api_key):
    res = requests.get(f"{BASE_URL}/search/companies?q={company_name}",
                       auth=(api_key, ""))
    res.raise_for_status()
    items = res.json().get("items", [])
    if not items:
        raise Exception("Company not found")
    return items[0]["company_number"], items[0]["title"]

def get_pscs(company_number, api_key):
    res = requests.get(f"{BASE_URL}/company/{company_number}/persons-with-significant-control",
                       auth=(api_key, ""))
    res.raise_for_status()
    return res.json().get("items", [])

def get_ownership_tree(company_name, api_key, visited=None):
    if visited is None:
        visited = set()

    company_number, name = search_company(company_name, api_key)
    if company_number in visited:
        return {"id": company_number, "label": name, "type": "UK Company", "children": []}

    visited.add(company_number)

    pscs = get_pscs(company_number, api_key)
    children = []
    for psc in pscs:
        if "name" in psc:
            label = psc["name"]
            type_ = "Individual"
        elif "corporate_name" in psc:
            label = psc["corporate_name"]
            type_ = "UK Company" if "registered_office_address" in psc else "Non-UK Company"
            if "company_number" in psc:
                try:
                    sub_tree = get_ownership_tree(psc["corporate_name"], api_key, visited)
                    children.append(sub_tree)
                    continue
                except:
                    pass
        else:
            label = "Unknown"
            type_ = "Unknown"

        children.append({
            "id": label,
            "label": label,
            "type": type_,
            "children": []
        })

    return {"id": company_number, "label": name, "type": "UK Company", "children": children}
