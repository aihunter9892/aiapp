#!/usr/bin/env python3
"""
Deploy the Elementor home template straight into WordPress via the plugin's
REST endpoint (claude-ai-trainer-globals v1.1+ must be active).

Usage:
  python3 deploy.py https://claudeaitrainer.com ADMIN_USER "APPLICATION PASSWORD"

Application password: WP Admin -> Users -> Profile -> Application Passwords
(spaces in the generated password are fine — quote it).
"""
import base64, json, os, sys, urllib.request

def main():
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(1)
    site, user, app_pw = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
    auth = base64.b64encode(f"{user}:{app_pw}".encode()).decode()
    hdrs = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    def call(method, path, payload=None):
        req = urllib.request.Request(site + path, method=method, headers=hdrs,
                                     data=json.dumps(payload).encode() if payload else None)
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())

    print("1) ping:", call("GET", "/wp-json/cat/v1/ping"))
    tpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-ai-trainer-home.json")
    tpl = json.load(open(tpl_path, encoding="utf-8"))
    print("2) importing home page ...")
    res = call("POST", "/wp-json/cat/v1/import-page", {
        "title": "Home", "slug": "home",
        "elementor": tpl["content"],
        "set_front": True,
        "template": "elementor_header_footer",
    })
    print("   ->", res)
    print("Done. Open", res.get("url"), "— and hard-refresh (Ctrl+Shift+R).")

if __name__ == "__main__":
    main()
