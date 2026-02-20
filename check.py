import requests
import hashlib
import os

TOPIC = "szumowski-alert"
STATE_FILE = "state.txt"

# POLSKIE SERWISY – pełna lista
URLS = [

    # Allegro kup teraz
    "https://allegro.pl/listing?string=szumowski+dookola+swiata",

    # Allegro licytacje
    "https://allegro.pl/listing?string=szumowski+dookola+swiata&offerTypeAuction=1",

    # Allegro Lokalnie
    "https://allegrolokalnie.pl/oferty/q-szumowski-dookola-swiata",

    # OLX
    "https://www.olx.pl/oferty/q-szumowski-dookola-swiata/",

    # Vinted
    "https://www.vinted.pl/catalog?search_text=szumowski+dookola+swiata",

    # Sprzedajemy
    "https://sprzedajemy.pl/szukaj?query=szumowski+dookola+swiata",

    # Gratka
    "https://gratka.pl/szukaj?query=szumowski+dookola+swiata",

    # Empik
    "https://www.empik.com/szukaj/produkt?query=szumowski%20dookola%20swiata",

    # TaniaKsiazka
    "https://www.taniaksiazka.pl/szukaj?query=szumowski+dookola+swiata",

    # Facebook Marketplace (publiczne wyniki)
    "https://www.facebook.com/marketplace/search/?query=szumowski%20dookola%20swiata"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        f.write("\n".join(state))


def page_active(response):
    # sprawdza czy strona istnieje
    if response.status_code != 200:
        return False

    text = response.text.lower()

    # typowe komunikaty o braku strony
    errors = [
        "nie znaleziono",
        "brak ogłoszeń",
        "no results",
        "page not found",
        "404"
    ]

    for e in errors:
        if e in text:
            return False

    return True


def main():
    known = load_state()
    new_known = set(known)

    for url in URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)

            if not page_active(r):
                continue

            text = r.text.lower()

            # warunki dopasowania
            if "szumowski" in text and "komik" in text or "dookola" in text:

                page_hash = hashlib.md5(text.encode()).hexdigest()

                if page_hash not in known:
                    notify(f"NOWA oferta możliwa:\n{url}")
                    new_known.add(page_hash)

        except:
            pass

    save_state(new_known)


if __name__ == "__main__":
    main()
