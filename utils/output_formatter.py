"""Formatiranje i cuvanje strukturisanog izlaza AI agenta (JSON + Markdown)."""

import json
import os
from datetime import datetime
from typing import Any, Dict

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def to_markdown(result: Dict[str, Any]) -> str:
    """Pretvara strukturisan rezultat agenta u citljivu Markdown tabelu za terminal."""
    lines = []
    lines.append(f"### Rezime upita\n{result.get('upit_rezime', '')}\n")

    preporuke = result.get("preporuke", [])
    if preporuke:
        lines.append("| Pruzalac | Usluga | Datum | Vreme | Cena (RSD) | Obrazlozenje |")
        lines.append("|---|---|---|---|---|---|")
        for r in preporuke:
            lines.append(
                f"| {r.get('pruzalac','')} | {r.get('usluga','')} | {r.get('datum','')} | "
                f"{r.get('vreme','')} | {r.get('cena_rsd','')} | {r.get('obrazlozenje','')} |"
            )
    else:
        lines.append("_Nema pronadjenih preporuka za zadati upit._")

    napomena = result.get("napomena", "")
    if napomena:
        lines.append(f"\n**Napomena:** {napomena}")

    return "\n".join(lines)


def save_result(result: Dict[str, Any], base_name: str = "preporuka") -> Dict[str, str]:
    """Cuva rezultat i kao .json i kao .md fajl u output/ direktorijumu. Vraca putanje."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.json")
    md_path = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown(result))

    return {"json": json_path, "markdown": md_path}
