import requests
import hashlib
import os

TOPIC = "szumowski-alert"
STATE_FILE = "state.txt"

URLS = [
    "https://allegro.pl/listing?string=szumowski+dookola+swiata",
    "https://allegro.pl/listing?string=szumowski+dookola+swiata&offerTypeAuction=1",
    "https://allegrolokalnie.pl/oferty/q-szumowski-dookola-swiata",
    "https://www.olx.pl/oferty/q-szumowski-dookola-swiata/",
    "https://www.vinted.pl/catalog?search_text=szumowski+dookola+swiata",
    "https://sprzedajemy.pl/szukaj?query=szumowski+dookola+swiata",
    "https://gratka.pl/szukaj?query=szumowski+dookola+swiata",
    "https://www.empik.com/szukaj/produkt?query=szumowski+dookola+swiata"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))


def get_hash(text):
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

        # ignoruj strony bez wyników
        if "brak wyników" in text or "nie znaleziono" in text:
            continue

        h = get_hash(text)
        new_state[url] = h

        if url in old_state:
            if old_state[url] != h:
                notify(f"Nowa oferta lub zmiana:\n{url}")

    except:
        pass

save_state(new_state)
