# ZakaziMe AI Scheduling Assistant

AI agent razvijen u okviru **Zadatka 3 (Razvoj AI agenta)**, tematski povezan sa projektom
**ZakaziMe** — platformom za online zakazivanje termina kod lokalnih pružalaca usluga
(frizerski/kozmetički saloni, spa/wellness centri, fitnes treneri, instruktori, majstori za
sitne popravke).

## Opis projekta

Agent prima zahtev korisnika izražen **prirodnim jezikom** (npr. *"Treba mi termin za masažu
sledeće nedelje ujutru, budžet do 3000 dinara"*), analizira ga uz pomoć velikog jezičkog
modela (LLM) i, na osnovu dostupnih podataka o pružaocima usluga i slobodnim terminima,
predlaže 1–3 najbolje odgovarajuća termina. Rezultat se prikazuje u terminalu i čuva u
strukturisanom formatu (JSON i Markdown).

## Funkcionalnosti

- Obrada korisničkog zahteva na prirodnom jeziku (srpski).
- Prompt engineering: strukturisan sistemski prompt koji definiše ulogu modela, zadatak i
  strogo definisan format izlaza (`agent/prompts.py`).
- Rad sa eksternim podacima: podaci o pružaocima usluga, cenama i slobodnim terminima
  učitavaju se iz `data/providers.json` (simulacija podataka platforme), uz filtriranje po
  ključnoj reči i budžetu (`data/data_loader.py`).
- Podrška za dva LLM provajdera (bira se u `.env`): **OpenAI** ili lokalni **Ollama** model.
- Tri načina unosa: interaktivni chat u terminalu, jednokratan upit preko komandne linije
  (`--query`) ili upit učitan iz fajla (`--input`).
- Strukturisan izlaz: JSON i Markdown tabela, prikazani u terminalu i sačuvani u `output/`.

## Struktura projekta

```
zakazime_ai_agent/
├── main.py                    # Ulazna tačka aplikacije (CLI)
├── agent/
│   ├── scheduling_agent.py    # AI logika (LangChain + LLM poziv, parsiranje odgovora)
│   └── prompts.py             # Sistemski i korisnički prompt (prompt engineering)
├── data/
│   ├── data_loader.py         # Rad sa eksternim podacima (učitavanje, filtriranje)
│   └── providers.json         # Eksterni podaci — pružaoci usluga i slobodni termini
├── utils/
│   └── output_formatter.py    # Formatiranje izlaza (JSON/Markdown) i čuvanje u fajl
├── output/                    # Generisani rezultati (JSON + Markdown), nije u git-u
├── requirements.txt
├── .env.example
├── .gitignore
└── sample_upit.txt            # Primer upita za --input režim
```

## Instalacija

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# otvoriti .env i uneti OPENAI_API_KEY (ili podesiti LLM_PROVIDER=ollama za lokalni model)
```

## Pokretanje

Interaktivni chat režim:
```bash
python main.py
```

Jednokratan upit preko komandne linije:
```bash
python main.py --query "Treba mi termin za šišanje ove nedelje, budžet do 2000 dinara"
```

Upit učitan iz fajla:
```bash
python main.py --input sample_upit.txt
```

Sa ograničenjem budžeta (RSD):
```bash
python main.py --query "Trening sa personalnim trenerom" --budget 3000
```

## Primer korišćenja

```
$ python main.py --query "Treba mi termin za masažu sledeće nedelje ujutru, budžet do 3500 dinara"

### Rezime upita
Klijent traži termin za relax/opuštajuću masažu u prepodnevnim satima, budžet do 3500 RSD.

| Pružalac | Usluga | Datum | Vreme | Cena (RSD) | Obrazloženje |
|---|---|---|---|---|---|
| Wellness centar Oaza | Relax masaža celog tela | 2026-09-10 | 09:00 | 3200 | Jutarnji termin u okviru budžeta, visoko ocenjen pružalac. |

(Rezultat sačuvan u: output/preporuka_20260910_090512.json i output/preporuka_20260910_090512.md)
```

## Korišćene biblioteke

- `langchain`, `langchain-core` — orkestracija poziva ka LLM-u
- `langchain-openai` — integracija sa OpenAI modelima
- `langchain-community`, `langchain-ollama` — podrška za lokalne modele preko Ollama
- `python-dotenv` — učitavanje konfiguracije iz `.env` fajla

## Napomena o bezbednosti

API ključevi se **nikada** ne čuvaju u kodu — isključivo u `.env` fajlu (koji je naveden u
`.gitignore` i ne komituje se na GitHub). Za deljenje konfiguracije koristi se `.env.example`
sa praznim/placeholder vrednostima.

## Veza sa projektom ZakaziMe

Ovaj agent predstavlja AI komponentu modula **"Kalendar i zakazivanje termina"** opisanog u
projektnom zadatku (Zadatak 1, Modul 3 i Modul 8 — AI Scheduling Assistant), i koristi isti
skup entiteta (pružaoci usluga, usluge, termini) koji je definisan tim dokumentom.
