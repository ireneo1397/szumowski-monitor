import requests
import hashlib
import os

TOPIC = "szumowski-alert"

URLS = [
    # Allegro
    "https://allegro.pl/listing?string=komik%20dookola%20swiata%20szumowski",

    # Allegro Lokalnie
    "https://allegrolokalnie.pl/oferty/q-komik-dookola-swiata-szumowski",

    # OLX
    "https://www.olx.pl/oferty/q-komik-dookola-swiata-szumowski/",

    # Vinted
    "https://www.vinted.pl/catalog?search_text=komik%20dookola%20swiata%20szumowski",

    # Facebook Marketplace
    "https://www.facebook.com/marketplace/search/?query=komik%20dookola%20swiata%20szumowski",

    # Empik
    "https://www.empik.com/szukaj/produkt?q=komik%20dookola%20swiata",

    # eBay
    "https://www.ebay.pl/sch/i.html?_nkw=komik+dookola+swiata+szumowski"
]

STATE_FILE = "state.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = ["komik", "szumowski"]

BAD_WORDS = [
    "404",
    "page not found",
    "nie znaleziono",
    "brak wyników",
    "oferta wygasła",
    "oferta nieaktualna"
]


def notify(message):
    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=message.encode("utf-8")
    )


def get_hash(text):
    # bierzemy tylko pierwszą część strony (wyniki)
    fragment = text[:60000]
    return hashlib.md5(fragment.encode()).hexdigest()


def page_valid(text):
    text = text.lower()
    for bad in BAD_WORDS:
        if bad in text:
            return False
    return True


def contains_keywords(text):
    text = text.lower()
    return all(word in text for word in KEYWORDS)


# wczytaj poprzedni stan
old_state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        for line in f:
            name, h = line.strip().split("|")
            old_state[name] = h

new_state = {}

for url in URLS:
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)

        if r.status_code != 200:
            continue

        text = r.text.lower()

        if not page_valid(text):
            continue

        if not contains_keywords(text):
            continue

        h = get_hash(text)
        new_state[url] = h

        # pierwsze uruchomienie — nie wysyłaj
        if url not in old_state:
            continue

        # zmiana zawartości (nowa oferta / zmiana ceny)
        if old_state[url] != h:
            notify(f"Zmiana lub nowa oferta:\n{url}")

    except:
        pass


# zapisz nowy stan
with open(STATE_FILE, "w") as f:
    for url, h in new_state.items():
        f.write(f"{url}|{h}\n")
