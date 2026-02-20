import requests
import re
import os
import unicodedata

TOPIC = "szumowski-alert"
STATE_FILE = "links.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URLS = [
    "https://allegro.pl/listing?string=komik+dookola+swiata+szumowski",
    "https://allegro.pl/listing?string=komik+dookola+swiata+szumowski&offerTypeAuction=1",
    "https://allegrolokalnie.pl/oferty/q-szumowski-dookola-swiata",
    "https://www.olx.pl/oferty/q-szumowski-dookola-swiata/",
    "https://www.vinted.pl/catalog?search_text=szumowski+dookola+swiata",
    "https://sprzedajemy.pl/szukaj?query=szumowski+dookola+swiata",
    "https://gratka.pl/szukaj?query=szumowski+dookola+swiata",
]

# --- normalizacja tekstu (usuwa polskie znaki) ---
def normalize(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text

# --- wysyłanie powiadomienia ---
def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))

# --- wczytaj zapisane linki ---
def load_links():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(f.read().splitlines())

# --- zapisz linki ---
def save_links(links):
    with open(STATE_FILE, "w") as f:
        for link in links:
            f.write(link + "\n")

# --- sprawdzanie czy to właściwa książka (TYLKO CZĘŚĆ 1) ---
def is_part_one(text):
    t = normalize(text)

    # musi zawierać:
    if "komik" not in t:
        return False
    if "dookola" not in t:
        return False
    if "swiata" not in t:
        return False
    if "szumowski" not in t:
        return False

    # NIE może zawierać:
    banned = [
        " 2",
        "czesc 2",
        "tom 2",
        "dookola swiata 2"
    ]

    for b in banned:
        if b in t:
            return False

    return True

# --- główna logika ---
seen_links = load_links()
new_links = set()

for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        text = r.text

        # znajdź linki ofert
        links = re.findall(r'https://[^\s"<>]+', text)

        for link in links:
            if link in seen_links:
                continue

            # sprawdź czy w okolicy linku jest tekst oferty
            fragment = text.lower()
            if link.lower() in fragment:
                start = fragment.find(link.lower())
                context = fragment[max(0, start-200):start+200]

                if is_part_one(context):
                    notify(f"NOWA OFERTA (część 1):\n{link}")
                    new_links.add(link)

    except:
        pass

# zapisz tylko nowe + stare
seen_links.update(new_links)
save_links(seen_links)
