#!/usr/bin/env python3
"""
wrap_with_password.py
======================
Wraps an existing HTML report with a JavaScript password prompt.
The full report content is stored inline — no server needed.
The password is hashed (SHA-256) so it's not visible in plain text in the file.

Usage:
  python3 scripts/wrap_with_password.py \
    --input  reports/health_report_Minko.html \
    --output reports/health_report_Minko_protected.html \
    --password yourpassword

The protected file can be hosted on GitHub Pages or anywhere static.
"""

import argparse
import hashlib
import sys
from pathlib import Path

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def wrap(input_path: Path, output_path: Path, password: str):
    report_html = input_path.read_text(encoding="utf-8")
    pw_hash     = sha256(password)

    # Escape backticks and backslashes for embedding in JS template literal
    escaped = report_html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    wrapper = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DNA Report — Protected</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0d0f14;
    color: #dde3ee;
    font-family: "SF Mono", "Fira Code", monospace;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }}
  .gate {{
    background: #161a22;
    border: 1px solid #262c38;
    border-radius: 10px;
    padding: 2.5rem 3rem;
    text-align: center;
    max-width: 380px;
    width: 90%;
  }}
  .gate h1 {{
    font-size: 1.4rem;
    color: #4fc3f7;
    margin-bottom: .4rem;
    letter-spacing: -.02em;
  }}
  .gate p {{
    font-size: .82rem;
    color: #7a8499;
    font-family: system-ui, sans-serif;
    margin-bottom: 1.5rem;
  }}
  input[type=password] {{
    width: 100%;
    background: #1e2534;
    border: 1px solid #262c38;
    border-radius: 6px;
    color: #dde3ee;
    font-family: "SF Mono", monospace;
    font-size: .95rem;
    padding: .65rem 1rem;
    margin-bottom: 1rem;
    outline: none;
    transition: border-color .15s;
  }}
  input[type=password]:focus {{ border-color: #4fc3f7; }}
  button {{
    width: 100%;
    background: #4fc3f7;
    color: #0d0f14;
    border: none;
    border-radius: 6px;
    font-family: "SF Mono", monospace;
    font-size: .9rem;
    font-weight: 700;
    padding: .65rem;
    cursor: pointer;
    transition: background .15s;
  }}
  button:hover {{ background: #81d4fa; }}
  .error {{
    color: #ef5350;
    font-size: .78rem;
    font-family: system-ui, sans-serif;
    margin-top: .75rem;
    display: none;
  }}
  #report {{ display: none; }}
</style>
</head>
<body>

<div class="gate" id="gate">
  <h1>⬡ DNA Report</h1>
  <p>This report is private.<br>Enter the password to view.</p>
  <input type="password" id="pw" placeholder="Password"
         onkeydown="if(event.key==='Enter') unlock()">
  <button onclick="unlock()">Unlock</button>
  <div class="error" id="err">Incorrect password — try again.</div>
</div>

<div id="report"></div>

<script>
  const HASH = "{pw_hash}";

  async function sha256(str) {{
    const buf  = await crypto.subtle.digest("SHA-256",
                   new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf))
                .map(b => b.toString(16).padStart(2,"0")).join("");
  }}

  async function unlock() {{
    const pw   = document.getElementById("pw").value;
    const hash = await sha256(pw);
    if (hash === HASH) {{
      document.getElementById("gate").style.display   = "none";
      const report = document.getElementById("report");
      report.style.display = "block";
      report.innerHTML = `{escaped}`;
    }} else {{
      const err = document.getElementById("err");
      err.style.display = "block";
      document.getElementById("pw").value = "";
      document.getElementById("pw").focus();
      setTimeout(() => err.style.display = "none", 3000);
    }}
  }}

  // Allow Enter key on load
  document.addEventListener("DOMContentLoaded", () => {{
    document.getElementById("pw").focus();
  }});
</script>
</body>
</html>"""

    output_path.write_text(wrapper, encoding="utf-8")
    print(f"OK  Protected report written → {output_path}")
    print(f"    Password hash (SHA-256): {pw_hash[:16]}...")
    print(f"    File size: {output_path.stat().st_size / 1024:.0f} KB")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",    required=True)
    parser.add_argument("--output",   required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)

    if not inp.exists():
        print(f"ERROR: input file not found: {inp}")
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    wrap(inp, out, args.password)

if __name__ == "__main__":
    main()