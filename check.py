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
    "https://www.empik.com/szukaj/produkt?query=szumowski+dookola+swiata"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def notify(message):
    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=message.encode("utf-8"),
        timeout=10
    )


def get_hash(text):
    # analizujemy tylko fragment strony (wyniki)
    fragment = text[:50000]
    return hashlib.md5(fragment.encode()).hexdigest()


def load_state():
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            for line in f:
                url, h = line.strip().split("|")
                state[url] = h
    return state


def save_state(state):
    with open(STATE_FILE, "w") as f:
        for url, h in state.items():
            f.write(f"{url}|{h}\n")


old_state = load_state()
new_state = {}

for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            continue

        text = r.text.lower()

        # ignoruj puste strony
        if (
            "brak wyników" in text
            or "nie znaleziono" in text
            or "0 wyników" in text
        ):
            continue

        h = get_hash(text)
        new_state[url] = h

        # jeśli strona była wcześniej i się zmieniła
        if url in old_state and old_state[url] != h:
            notify(f"Nowa oferta lub zmiana:\n{url}")

    except:
        pass

save_state(new_state)
