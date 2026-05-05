import sys
import os
import re
import json

# This script patches the python-jobspy library to restore Glassdoor functionality
# by using the modern BFF endpoint and curl_cffi for Cloudflare bypass.

file_path = os.path.expanduser("~/survivalstack/Vanguard/.venv/lib/python3.12/site-packages/jobspy/glassdoor/__init__.py")

if not os.path.exists(file_path):
    print(f"Error: Could not find JobSpy Glassdoor source at {file_path}")
    sys.exit(1)

with open(file_path, 'r') as f:
    content = f.read()

# 1. Add curl_cffi import
if "from curl_cffi import requests as curl_requests" not in content:
    content = content.replace("import requests", "import requests\nfrom curl_cffi import requests as curl_requests")

# 2. Patch _add_payload to return variables directly for BFF
old_add_payload = r'return json\.dumps\(\[payload\]\)'
if re.search(old_add_payload, content):
    content = re.sub(old_add_payload, 'return json.dumps(payload["variables"])', content)

# 3. Patch _fetch_jobs_page to use BFF endpoint
old_fetch = r'response = self\.session\.post\(\n\s+f"\{self\.base_url\}/graph",\n\s+timeout_seconds=15,\n\s+data=payload,\n\s+\)'
new_fetch = """            # Use curl_cffi to bypass Cloudflare and use BFF endpoint
            response = curl_requests.post(
                f"{self.base_url}/job-search-next/bff/jobSearchResultsQuery",
                headers=self.session.headers,
                impersonate="chrome",
                timeout=15,
                data=payload,
            )"""

if re.search(old_fetch, content):
    content = re.sub(old_fetch, new_fetch, content)

# 4. Patch res_json parsing
content = content.replace("res_json = response.json()[0]", "res_json = response.json()")

# 5. Patch _get_csrf_token and _get_location to use curl_cffi
content = content.replace('res = self.session.get(url)', 'res = curl_requests.get(url, headers=self.session.headers, impersonate="chrome", timeout=15)')
content = content.replace('res = self.session.get(f"{self.base_url}/Job/computer-science-jobs.htm")', 'res = curl_requests.get(f"{self.base_url}/Job/index.htm", headers=self.session.headers, impersonate="chrome", timeout=15)')

with open(file_path, 'w') as f:
    f.write(content)

print("Glassdoor patched successfully via scripts/patches/jobspy_glassdoor_bff.py")
