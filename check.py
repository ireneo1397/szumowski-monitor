import requests
import hashlib
import os

TOPIC = "szumowski-alert"
STATE_FILE = "state.txt"

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
    "https://www.empik.com/szukaj/produkt?q=szumowski+dookola+swiata"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = [
    "szumowski",
    "dookola",
    "komik"
]


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


def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def page_active(response):
    # sprawdza czy strona istnieje
    return response.status_code == 200 and len(response.text) > 1000


old_state = load_state()
new_state = set()

for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)

        if not page_active(r):
            continue

        text = r.text.lower()

        if all(k in text for k in KEYWORDS):
            page_hash = hash_text(text)
            new_state.add(page_hash)

            if page_hash not in old_state:

                message = f"Nowa oferta możliwa:\n{url}"

                # dodatkowa informacja o licytacji
                if "offertypeauction" in url:
                    message += "\nTyp: LICYTACJA"

                notify(message)

    except Exception:
        continue

save_state(new_state)
