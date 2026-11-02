"""Render RESEARCH_PAPER.md to a self-contained HTML page and a PDF via headless Edge/Chrome.

Markdown and LaTeX are rendered client-side (marked + KaTeX from jsDelivr), so the
browser needs network access the first time. Figures are referenced from the repository.

Usage:
    python scripts/reporting/render_paper_pdf.py [--browser PATH]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "RESEARCH_PAPER.md"
HTML_OUT = ROOT / "output" / "paper" / "RESEARCH_PAPER.html"
PDF_OUT = ROOT / "output" / "pdf" / "RESEARCH_PAPER.pdf"

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge", "google-chrome", "chromium", "chromium-browser",
]

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Spend It Together or Spend It Big? (Project Agere)</title>
<base href="{base}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<style>
  @page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
  body {{ font-family: "Georgia", "Times New Roman", serif; font-size: 10.4pt; line-height: 1.45; color: #1b2733; max-width: 180mm; margin: 0 auto; }}
  h1 {{ font-size: 19pt; line-height: 1.2; color: #16324f; margin: 0 0 6pt; }}
  h2 {{ font-size: 14pt; color: #16324f; border-bottom: 1px solid #c9d2da; padding-bottom: 2pt; margin-top: 20pt; page-break-after: avoid; }}
  h3 {{ font-size: 11.5pt; color: #16324f; margin-top: 14pt; page-break-after: avoid; }}
  p, li {{ text-align: justify; }}
  table {{ border-collapse: collapse; width: 100%; margin: 8pt 0 10pt; font-family: "Segoe UI", Arial, sans-serif; font-size: 8.2pt; page-break-inside: avoid; }}
  th {{ background: #16324f; color: white; font-weight: 600; }}
  th, td {{ border: 1px solid #c9d2da; padding: 3pt 4pt; vertical-align: top; text-align: left; }}
  tr:nth-child(even) td {{ background: #f3f6f8; }}
  img {{ display: block; max-width: 100%; margin: 8pt auto 2pt; page-break-inside: avoid; }}
  p:has(> img) {{ text-align: center; font-size: 8.5pt; color: #4a5866; page-break-inside: avoid; }}
  .caption {{ text-align: center; font-size: 8.6pt; color: #4a5866; font-style: italic; margin: 0 0 10pt; }}
  pre {{ background: #f3f6f8; border: 1px solid #d5dbe1; padding: 6pt; font-size: 7.4pt; line-height: 1.3; white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }}
  code {{ font-family: Consolas, "Courier New", monospace; font-size: 8.6pt; }}
  blockquote {{ border-left: 3px solid #007b7f; margin: 8pt 0; padding: 2pt 10pt; background: #eef6f6; }}
  hr {{ border: 0; border-top: 1px solid #c9d2da; margin: 14pt 0; }}
  .katex-display {{ margin: 6pt 0; }}
</style></head>
<body><div id="content">Renderingâ€¦</div>
<script id="md" type="text/markdown">{markdown}</script>
<script>
(function () {{
  let src = document.getElementById('md').textContent;
  const keep = [];
  const stash = (s) => {{ keep.push(s); return 'QQKEEP' + (keep.length - 1) + 'QQ'; }};
  src = src.replace(/```[\\s\\S]*?```/g, stash);
  src = src.replace(/`[^`\\n]+`/g, stash);
  const math = [];
  const mstash = (tex, display) => {{ math.push([tex, display]); return 'QQMATH' + (math.length - 1) + 'QQ'; }};
  src = src.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (_, t) => mstash(t, true));
  src = src.replace(/\\$([^$\\n]+?)\\$/g, (_, t) => mstash(t, false));
  src = src.replace(/QQKEEP(\\d+)QQ/g, (_, i) => keep[+i]);
  let out = marked.parse(src, {{ gfm: true }});
  out = out.replace(/QQMATH(\\d+)QQ/g, (_, i) => {{
    const [tex, display] = math[+i];
    try {{ return katex.renderToString(tex, {{ displayMode: display, throwOnError: false }}); }}
    catch (e) {{ return tex; }}
  }});
  const root = document.getElementById('content');
  root.innerHTML = out;
  root.querySelectorAll('p > img').forEach((img) => {{
    if (img.alt) {{
      const cap = document.createElement('div');
      cap.className = 'caption';
      cap.textContent = img.alt;
      img.parentElement.after(cap);
    }}
  }});
  document.title = 'Spend It Together or Spend It Big? (Project Agere)';
  window.__rendered = true;
}})();
</script></body></html>
"""


def find_browser(explicit: str | None) -> str:
    for c in ([explicit] if explicit else []) + CANDIDATES:
        if c and (Path(c).exists() or shutil.which(c)):
            return c
    raise SystemExit("No Edge/Chrome/Chromium browser found; pass --browser")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser")
    ap.add_argument("--html-only", action="store_true", help="Write HTML for the verified Playwright renderer without printing a PDF")
    args = ap.parse_args()
    md = SRC.read_text(encoding="utf-8").replace("</script", "<\\/script")
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(TEMPLATE.format(base="../../", markdown=md),
                        encoding="utf-8")
    if args.html_only:
        print(f"HTML: {HTML_OUT}")
        return
    browser = find_browser(args.browser)
    subprocess.run(
        [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
         "--virtual-time-budget=30000", f"--print-to-pdf={PDF_OUT}", HTML_OUT.as_uri()],
        check=True, timeout=300,
    )
    print(f"HTML: {HTML_OUT}\nPDF:  {PDF_OUT} ({PDF_OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
