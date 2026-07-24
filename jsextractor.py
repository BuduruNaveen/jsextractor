#!/usr/bin/env python3
import re
import sys
import json
import requests
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_js(url, timeout=10):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[-] Failed to fetch {url}: {e}", file=sys.stderr)
        return ""

def extract_js_urls(html, base_url):
    patterns = [
        r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']',
        r'src\s*=\s*["\']([^"\']+\.js[^"\']*)["\']',
        r'import\s+["\']([^"\']+\.js[^"\']*)["\']',
        r'require\(["\']([^"\']+\.js[^"\']*)["\']\)',
        r'url\s*\(\s*["\']([^"\']+\.js[^"\']*)["\']\)',
        r'["\']([^"\']+\.js(?:\\?[^"\']*)?)["\']',
    ]
    urls = set()
    for pat in patterns:
        for match in re.finditer(pat, html, re.IGNORECASE):
            raw = match.group(1).strip()
            if raw:
                absolute = urljoin(base_url, raw)
                urls.add(absolute)

    parsed_base = urlparse(base_url)
    same_origin = []
    external = []
    for u in sorted(urls):
        if not u.startswith(("http://", "https://")):
            continue
        p = urlparse(u)
        if p.netloc == parsed_base.netloc or not p.netloc:
            if u.endswith(".js"):
                same_origin.append(u)
        else:
            external.append(u)

    return same_origin, external

def process_url(url, timeout=10):
    print(f"\n[*] Processing: {url}")
    html = fetch_js(url, timeout)
    if not html:
        return [], []
    same, ext = extract_js_urls(html, url)

    # Also discover JS from inline scripts that load more JS
    inline_js = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html, re.IGNORECASE)
    for block in inline_js:
        for match in re.finditer(r'["\']([^"\']+\.js[^"\']*?)["\']', block):
            raw = match.group(1)
            absolute = urljoin(url, raw)
            if absolute not in same and absolute not in ext:
                p = urlparse(absolute)
                if p.netloc == urlparse(url).netloc:
                    same.append(absolute)
                else:
                    ext.append(absolute)

    return same, ext

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single URL:  python js_extractor.py https://example.com")
        print("  Multiple:    python js_extractor.py urls.txt")
        print("  JSON output: python js_extractor.py https://example.com --json")
         print("@naveenventure <3")
        sys.exit(1)

    output_json = "--json" in sys.argv

    sources = []
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("--"):
        arg = sys.argv[1]
        if arg.startswith(("http://", "https://")):
            sources = [arg]
        else:
            try:
                with open(arg) as f:
                    sources = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"[-] File not found: {arg}", file=sys.stderr)
                sys.exit(1)

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        fut_map = {executor.submit(process_url, url): url for url in sources}
        for fut in as_completed(fut_map):
            url = fut_map[fut]
            same, ext = fut.result()
            results[url] = {"same_origin": same, "external": ext}

    if output_json:
        print(json.dumps(results, indent=2))
        return

    for url, data in results.items():
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        if data["same_origin"]:
            print(f"\n[+] Same-origin JS ({len(data['same_origin'])}):")
            for js in data["same_origin"]:
                print(f"  {js}")
        if data["external"]:
            print(f"\n[+] External JS ({len(data['external'])}):")
            for js in data["external"]:
                print(f"  {js}")
        if not data["same_origin"] and not data["external"]:
            print("  No JS files found.")

    total = sum(len(d["same_origin"]) + len(d["external"]) for d in results.values())
    print(f"\n{'='*60}")
    print(f"Total JS URLs found: {total}")

if __name__ == "__main__":
    main()
