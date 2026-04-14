#!/usr/bin/env python3
import os, json, requests, argparse, textwrap

def load_diff(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(diff):
    return textwrap.dedent(f"""
    You are a senior software engineer performing an enterprise-grade pull request review.

Review the provided git diff for correctness, reliability, security, performance, maintainability, test quality, and operational risk.

Rules:

* Be specific, skeptical, and evidence-based.
* Report only issues supported by the diff.
* Prioritize real risks over style comments.
* Separate confirmed issues from open questions.
* Consider backward compatibility, failure handling, observability, and rollout safety.

Return markdown only.

Use these sections exactly:

## PR Summary

## Risk Level

## Findings

## Suggested Fixes

## Test Recommendations

## Merge Recommendation

Requirements:

* PR Summary: 2 to 4 sentences.
* Risk Level: Low / Medium / High / Critical with one-line reason.
* Findings: only the most important issues. For each finding include:

  * Severity
  * Title
  * Why it matters
  * Evidence
  * Recommendation
  * Confidence
    * Suggested Fixes: include patch-style snippets only when confident.
    * Test Recommendations: list the highest-value missing tests.
    * Merge Recommendation: Approve / Approve with minor comments / Request changes / Block.

    If there are no significant issues, say so clearly.
    If context is missing, state the limitation explicitly.
    If a risk is uncertain, label it as Open Question.

    Diff:
    {{diff}}

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