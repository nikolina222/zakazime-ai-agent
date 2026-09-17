"""
ZakaziMe AI Scheduling Assistant - ulazna tacka aplikacije.

Pokretanje:
    python main.py                              -> interaktivni chat rezim (terminal)
    python main.py --query "Treba mi termin..."  -> jednokratni upit (komandna linija)
    python main.py --input upit.txt              -> upit ucitan iz fajla
    python main.py --query "..." --budget 3000    -> upit sa ogranicenjem budzeta (RSD)

Za detaljno uputstvo videti README.md.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from agent.scheduling_agent import get_recommendation, SchedulingAgentError
from utils.output_formatter import to_markdown, save_result

load_dotenv()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ZakaziMe AI Scheduling Assistant - pomaze u pronalazenju termina."
    )
    parser.add_argument(
        "--query", "-q", type=str, default=None,
        help="Zahtev za zakazivanje na prirodnom jeziku (jednokratni rezim).",
    )
    parser.add_argument(
        "--input", "-i", type=str, default=None,
        help="Putanja do tekstualnog fajla koji sadrzi korisnicki upit.",
    )
    parser.add_argument(
        "--budget", "-b", type=int, default=None,
        help="Maksimalan budzet u RSD (opciono).",
    )
    return parser


def run_single_query(user_query: str, budget: int | None) -> None:
    try:
        result = get_recommendation(user_query, max_price_rsd=budget)
    except SchedulingAgentError as exc:
        print(f"\n[GRESKA] {exc}\n", file=sys.stderr)
        sys.exit(1)

    print("\n" + to_markdown(result) + "\n")
    paths = save_result(result)
    print(f"(Rezultat sacuvan u: {paths['json']} i {paths['markdown']})")


def run_interactive_loop() -> None:
    print("=== ZakaziMe AI Scheduling Assistant ===")
    print("Opisite zahtev za zakazivanje termina (ili upisite 'kraj' za izlaz).\n")
    while True:
        try:
            user_query = input("Vi: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nPrekid rada. Doviđenja!")
            break

        if user_query.lower() in {"kraj", "exit", "quit"}:
            print("Doviđenja!")
            break
        if not user_query:
            continue

        run_single_query(user_query, budget=None)


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.input:
        if not os.path.exists(args.input):
            print(f"[GRESKA] Fajl '{args.input}' ne postoji.", file=sys.stderr)
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            query = f.read().strip()
        run_single_query(query, budget=args.budget)
    elif args.query:
        run_single_query(args.query, budget=args.budget)
    else:
        run_interactive_loop()


if __name__ == "__main__":
    main()
