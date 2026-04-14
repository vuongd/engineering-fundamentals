#!/usr/bin/env python3
import os, json, requests, argparse, textwrap

def load_diff(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(diff):
    return textwrap.dedent(f"""
    Review this git unified diff and provide:
    1) 2-3 line PR summary.
    2) Bullet list of potential issues (bug, security, style) with severity.
    3) Suggested fixes (code snippets or patch hunks) when applicable.
    4) Confidence and next steps.

    Diff:
    {diff}
    """)

def call_generativelanguage(api_key, model, prompt, max_tokens=512, temperature=0.0):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": int(max_tokens),
            "temperature": float(temperature)
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def extract_text(resp):
    try:
        return resp["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return json.dumps(resp, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", required=True)
    p.add_argument("--model", default="gemini-3-flash-preview")
    p.add_argument("--diff-file", default="pr.diff")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--out-file", default="pr_summary.txt")
    args = p.parse_args()

    diff = load_diff(args.diff_file)
    if not diff.strip():
        with open(args.out_file, "w", encoding="utf-8") as f:
            f.write("No changes to review.\n")
        return

    prompt = build_prompt(diff)
    resp = call_generativelanguage(args.api_key, args.model, prompt, args.max_tokens)
    text = extract_text(resp)

    with open(args.out_file, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    main()