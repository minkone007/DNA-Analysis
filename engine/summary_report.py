#!/usr/bin/env python3
"""
summary_report.py
Generates a nice HTML summary from all_traits_summary.json
"""

import json
from pathlib import Path
from datetime import date

def generate_summary_html():
    summary_path = Path("reports/all_traits_summary.json")
    if not summary_path.exists():
        print("No summary.json found. Run the PRS engine first.")
        return

    with open(summary_path) as f:
        traits = json.load(f)

    # Sort by confidence score descending
    traits.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNA Analysis Summary - {date.today().strftime("%B %d, %Y")}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 40px; background: #f8f9fa; }}
        h1 {{ color: #1e3a8a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #1e3a8a; color: white; }}
        tr:nth-child(even) {{ background: #f1f5f9; }}
        .high {{ color: #166534; font-weight: bold; }}
        .medium {{ color: #854d0e; }}
        .low {{ color: #991b1b; }}
    </style>
</head>
<body>
    <h1>DNA Analysis Summary</h1>
    <p><strong>Generated:</strong> {date.today().strftime("%B %d, %Y")} | <strong>Traits Analyzed:</strong> {len(traits)}</p>
    
    <table>
        <tr>
            <th>Trait</th>
            <th>Prediction</th>
            <th>Raw Score</th>
            <th>Percentile</th>
            <th>Confidence</th>
            <th>SNPs Used</th>
        </tr>
"""

    for t in traits:
        conf_class = "high" if t["confidence_score"] >= 70 else "medium" if t["confidence_score"] >= 50 else "low"
        html += f"""
        <tr>
            <td><strong>{t['trait']}</strong></td>
            <td>{t['prediction']}</td>
            <td>{t['raw_score']}</td>
            <td>{t['percentile']}</td>
            <td class="{conf_class}">{t['confidence_label']} ({t['confidence_score']})</td>
            <td>{t['snps_scored']}/{t['snps_available']}</td>
        </tr>"""

    html += """
    </table>
</body>
</html>"""

    output_path = Path("reports/summary_report.html")
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Summary report generated: {output_path}")

    return output_path


if __name__ == "__main__":
    generate_summary_html()