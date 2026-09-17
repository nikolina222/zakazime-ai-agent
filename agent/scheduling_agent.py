"""
AI logika agenta - ZakaziMe AI Scheduling Assistant.

Koristi LangChain za komunikaciju sa velikim jezickim modelom (LLM), uz strukturisan
prompt (agent/prompts.py) i podatke iz platforme (data/data_loader.py), kako bi na
osnovu prirodno-jezickog zahteva korisnika predlozio najbolje dostupne termine.

Podrzana su dva provajdera modela, birana preko .env fajla (LLM_PROVIDER):
  - "openai": ChatOpenAI (potreban OPENAI_API_KEY)
  - "ollama": lokalni model preko Ollama servera (potreban pokrenut Ollama, bez API kljuca)
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from data.data_loader import (
    load_providers,
    flatten_available_slots,
    filter_offers,
    offers_to_context_text,
)


class SchedulingAgentError(Exception):
    """Greska u radu AI agenta (konfiguracija, poziv modela ili parsiranje odgovora)."""


def _build_llm():
    """Kreira LLM instancu na osnovu konfiguracije iz .env fajla."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SchedulingAgentError(
                "OPENAI_API_KEY nije podesen u .env fajlu (videti .env.example)."
            )
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model_name, api_key=api_key, temperature=0.2)

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model_name, base_url=base_url, temperature=0.2)

    raise SchedulingAgentError(
        f"Nepoznat LLM_PROVIDER '{provider}'. Podrzane vrednosti su: 'openai', 'ollama'."
    )


def _extract_json(raw_text: str) -> Dict[str, Any]:
    """
    Izvlaci i parsira JSON iz odgovora modela. Model treba da vrati cist JSON, ali
    ova funkcija tolerise slucaj da model ipak doda markdown ogradu (```json ... ```)
    oko odgovora.
    """
    text = raw_text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchedulingAgentError(
            f"Model nije vratio validan JSON odgovor. Greska pri parsiranju: {exc}\n"
            f"Sirovi odgovor modela:\n{raw_text}"
        )


def _guess_category_keyword(user_query: str) -> Optional[str]:
    """
    Jednostavna heuristika za pred-filtriranje eksternih podataka na osnovu
    kljucnih reci iz upita (smanjuje kolicinu konteksta poslatog modelu).
    Finalni izbor i dalje pravi LLM na osnovu preostalih ponuda.
    """
    keywords = [
        "sisanje", "farbanje", "manikir", "masaza", "trening", "fitnes",
        "matematik", "instrukcij", "popravk", "montaza", "kozmet", "spa",
    ]
    lowered = user_query.lower()
    for kw in keywords:
        if kw in lowered:
            return kw
    return None


def get_recommendation(
    user_query: str,
    providers_path: Optional[str] = None,
    max_price_rsd: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Glavna funkcija AI agenta.

    1. Ucitava eksterne podatke o pruzaocima/uslugama/terminima.
    2. Filtrira ih na osnovu jednostavne heuristike i (opciono) budzeta.
    3. Salje strukturisan prompt modelu (uloga + zadatak + format izlaza).
    4. Parsira i vraca strukturisan odgovor (dict spreman za JSON/Markdown izlaz).
    """
    if not user_query or not user_query.strip():
        raise SchedulingAgentError("Korisnicki upit ne sme biti prazan.")

    providers = load_providers(providers_path) if providers_path else load_providers()
    all_offers = flatten_available_slots(providers)

    category_kw = _guess_category_keyword(user_query)
    filtered = filter_offers(
        all_offers, category_keyword=category_kw, max_price_rsd=max_price_rsd
    )
    # ako je filter previse suzio ponudu (ili heuristika nije prepoznala kategoriju),
    # radije posalji modelu ceo skup ponuda nego prazan kontekst
    offers_for_context = filtered if filtered else all_offers

    offers_context = offers_to_context_text(offers_for_context)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        user_query=user_query, offers_context=offers_context
    )

    llm = _build_llm()

    from langchain_core.messages import SystemMessage, HumanMessage

    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_prompt)]
    response = llm.invoke(messages)
    raw_text = response.content if hasattr(response, "content") else str(response)

    result = _extract_json(raw_text)
    result.setdefault("upit_rezime", user_query)
    result.setdefault("preporuke", [])
    result.setdefault("napomena", "")
    return result
