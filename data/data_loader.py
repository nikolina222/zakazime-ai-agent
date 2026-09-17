"""
Modul za rad sa eksternim podacima.

U produkcionoj verziji platforme ZakaziMe ovi podaci bi dolazili iz prave
baze podataka (PostgreSQL) preko backend API-ja. Za potrebe ovog AI agenta,
podaci o pruzaocima usluga, njihovim uslugama i slobodnim terminima ucitavaju
se iz eksternog JSON fajla (data/providers.json), sto simulira eksterni izvor
podataka koji agent obradjuje.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "providers.json")


def load_providers(path: str = DEFAULT_DATA_PATH) -> List[Dict[str, Any]]:
    """Ucitava listu pruzalaca usluga (sa uslugama i slobodnim terminima) iz JSON fajla."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Fajl sa eksternim podacima nije pronadjen: {path}"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_available_slots(providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pretvara ugnjezdenu strukturu (pruzalac -> usluge -> slobodni termini) u ravnu
    listu ponuda, spremnu za filtriranje i prosledjivanje modelu kao kontekst.
    """
    flat = []
    for provider in providers:
        services_by_id = {s["service_id"]: s for s in provider.get("services", [])}
        for slot in provider.get("available_slots", []):
            service = services_by_id.get(slot["service_id"])
            if not service:
                continue
            flat.append({
                "provider_id": provider["provider_id"],
                "provider_name": provider["name"],
                "category": provider["category"],
                "location": provider["location"],
                "rating": provider["rating"],
                "service_name": service["name"],
                "duration_min": service["duration_min"],
                "price_rsd": service["price_rsd"],
                "date": slot["date"],
                "time": slot["time"],
            })
    return flat


def filter_offers(
    offers: List[Dict[str, Any]],
    category_keyword: Optional[str] = None,
    max_price_rsd: Optional[int] = None,
    date_from: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filtrira ponude po kljucnoj reci kategorije/naziva usluge, maksimalnoj ceni
    i/ili najranijem datumu. Svi parametri su opcioni - koriste se samo oni
    koje agent prepozna iz korisnickog upita.
    """
    result = offers

    if category_keyword:
        kw = category_keyword.lower()
        result = [
            o for o in result
            if kw in o["category"].lower() or kw in o["service_name"].lower()
        ]

    if max_price_rsd is not None:
        result = [o for o in result if o["price_rsd"] <= max_price_rsd]

    if date_from:
        try:
            cutoff = datetime.strptime(date_from, "%Y-%m-%d")
            result = [
                o for o in result
                if datetime.strptime(o["date"], "%Y-%m-%d") >= cutoff
            ]
        except ValueError:
            pass  # ako datum nije validan, ignorisi filter po datumu

    return result


def offers_to_context_text(offers: List[Dict[str, Any]], limit: int = 25) -> str:
    """Formatira listu ponuda u kompaktan tekst koji se prosledjuje modelu kao kontekst."""
    lines = []
    for o in offers[:limit]:
        lines.append(
            f"- [{o['provider_id']}] {o['provider_name']} ({o['category']}, {o['location']}, "
            f"ocena {o['rating']}) | usluga: {o['service_name']} ({o['duration_min']} min) | "
            f"cena: {o['price_rsd']} RSD | termin: {o['date']} {o['time']}"
        )
    return "\n".join(lines) if lines else "(Nema dostupnih ponuda za zadate kriterijume.)"
