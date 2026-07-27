import json, argparse, glob
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

def clean_text(text):
    if not text: return ""
    cleaned = str(text).replace("[[", "").replace("]]", "")
    return (cleaned[:150] + '...') if len(cleaned) > 150 else cleaned

def load_all_results():
    all_data = defaultdict(list)
    result_files = glob.glob(str(RESULTS_DIR / "*_results.json"))
    for file_path in result_files:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                if "results" in data:
                    for item in data["results"]:
                        category = item.get("category", Path(file_path).stem.replace("_results", "").capitalize())
                        all_data[category].append(item)
                elif "top_snps" in data:
                    category = data.get("trait", "General").capitalize()
                    for snp in data["top_snps"]:
                        snp["category"] = category
                        snp["interpretation"] = snp.get("risk_info", "No interpretation.")
                        all_data[category].append(snp)
            except json.JSONDecodeError:
                continue
    return all_data

def main(person_name):
    report_data = load_all_results()
    categories = sorted(report_data.keys()) 
    
    # Updated path to look inside the person's specific results folder
    summary_path = RESULTS_DIR / person_name / "personal_summary.json"
    
    # 2. Build Dashboard with INLINE styles (no separate <style> block needed)
    dashboard_html = """
    <h2 style="font-family: sans-serif;">EXECUTIVE DASHBOARD</h2>
    <table style="border-collapse: collapse; width: 100%; font-family: sans-serif; border: 1px solid #ccc;">
    """
    
    if summary_path.exists():
        with open(summary_path, 'r') as f:
            summary = json.load(f)
            for category, traits in summary.items():
                dashboard_html += f"""
                <tr>
                    <th colspan="2" style="background-color: #f2f2f2; text-align: left; padding: 10px; border: 1px solid #ccc;">
                        {category.replace('_', ' ').upper()}
                    </th>
                </tr>
                """
                for trait, info in traits.items():
                    if isinstance(info, dict):
                        details = ", ".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in info.items()])
                    else:
                        details = str(info)
                    dashboard_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ccc;">{trait.replace('_', ' ').capitalize()}</td>
                        <td style="padding: 8px; border: 1px solid #ccc;">{details}</td>
                    </tr>
                    """
    dashboard_html += "</table><br><hr>"

    # 3. Combine content
    html_content = f"<html><body><h1 style='font-family: sans-serif;'>{person_name} DNA Report</h1>{dashboard_html}"
    
    for cat in categories:
        entries = report_data[cat]
        html_content += f"<h2>{cat.upper()}</h2><ul>"
        for e in entries:
            rsid = e.get('rsid', 'Unknown')
            desc = e.get('interpretation') or e.get('risk_info') or "Genotype detected, no specific risk data mapped."
            if desc.startswith(rsid):
                desc = "Genotype detected: " + e.get('your_genotype', 'Unknown')
            html_content += f"<li><strong>{rsid}</strong>: {clean_text(desc)}</li>"
        html_content += "</ul>"
    
    with open(RESULTS_DIR / f"health_report_{person_name}.html", "w") as f:
        f.write(html_content + "</body></html>")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--person", required=True)
    args = parser.parse_args()
    main(args.person)