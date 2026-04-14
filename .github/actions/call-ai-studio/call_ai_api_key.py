#!/usr/bin/env python3
import argparse, os, json, requests, textwrap

def load_diff(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(diff):
    return f"""You are an assistant that reviews a git unified diff for correctness, security, style, and tests.
Provide:
1) 2-3 line PR summary.
2) Bullet list of potential issues (bug/security/style), each with severity.
3) Suggested fixes (code snippets or patch hunks) where applicable.
4) Confidence and next steps.

Diff:
{diff}
"""

def call_ai_api_key(api_key, model, prompt, max_tokens=800):
    # Use AI Studio REST endpoint with API key auth (example endpoint — adapt if your region/endpoint differs)
    # Some accounts use an OpenAI-compatible endpoint; adjust URL format per your Google AI Studio docs.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generate?key={api_key}"
    payload = {
        "instances": [{"content": prompt}],
        "parameters": {"maxOutputTokens": int(max_tokens)}
    }


    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()

def extract_text(resp):
    # Handle common response shapes. Adjust to match your model's response schema.
    if isinstance(resp, dict):
        if "predictions" in resp and resp["predictions"]:
            pred = resp["predictions"][0]
            if isinstance(pred, dict):
                return pred.get("content") or pred.get("output") or json.dumps(pred)
            return str(pred)
        if "outputs" in resp:
            return json.dumps(resp["outputs"])
    return json.dumps(resp)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--diff-file", default="pr.diff")
    p.add_argument("--max-tokens", default=800)
    p.add_argument("--out-file", default="pr_summary.txt")
    args = p.parse_args()

    diff = load_diff(args.diff_file)
    if not diff.strip():
        with open(args.out_file, "w", encoding="utf-8") as f:
            f.write("No changes to review.\n")
        return

    prompt = build_prompt(diff)
    resp = call_ai_api_key(args.api_key, args.model, prompt, args.max_tokens)
    text = extract_text(resp)
    with open(args.out_file, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    main()
