import requests
import re
import json
import os
import time

TOPIC = "szumowski-alert"
STATE_FILE = "offers_state.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# --- WIELE ZAPYTAŃ (STAŁE) ---
QUERIES = [
    "szumowski+dookola+swiata",
    "komik+dookola+swiata",
    "komik+szumowski",
    "piotr+szumowski+ksiazka",
    "szumowski+komik"
]

# --- POLSKIE SERWISY ---
BASE_URLS = [
    "https://allegro.pl/listing?string={}",
    "https://allegro.pl/listing?string={}&offerTypeAuction=1",
    "https://www.olx.pl/oferty/q-{}/",
    "https://www.vinted.pl/catalog?search_text={}",
    "https://sprzedajemy.pl/szukaj?query={}",
    "https://gratka.pl/szukaj?query={}"
]

SEARCH_URLS = []
for q in QUERIES:
    for base in BASE_URLS:
        SEARCH_URLS.append(base.format(q))


# --- POWIADOMIENIE ---
def notify(msg):
    try:
        requests.post(
            f"https://ntfy.sh/{TOPIC}",
            data=msg.encode("utf-8"),
            timeout=10
        )
    except:
        pass


# --- STAN ---
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


# --- CENA ---
def get_price(text):
    m = re.search(r'(\d[\d\s]{0,6}[,\.]?\d{0,2})\s?zł', text)
    if m:
        price = m.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(price)
        except:
            return None
    return None


# --- FILTR KSIĄŻKI (CZĘŚĆ 1) ---
def valid_book(title):
    title = title.lower()

    # musi zawierać coś z tego
    keywords = [
        "szumowski",
        "komik dookoła",
        "komik dookola"
    ]

    if not any(k in title for k in keywords):
        return False

    # wykluczenie części 2
    exclude = [
        "część 2",
        "czesc 2",
        "tom 2",
        "t.2",
        "cz.2",
        "część druga"
    ]

    for e in exclude:
        if e in title:
            return False

    return True


# --- WYCIĄGANIE LINKÓW ---
def extract_links(html):
    links = set()

    patterns = [
        r'https://allegro\.pl/oferta/[^\"]+',
        r'https://www\.olx\.pl/[^\"]+\.html',
        r'https://www\.vinted\.pl/items/[^\"]+',
        r'https://sprzedajemy\.pl/[^\"]+',
        r'https://gratka\.pl/[^\"]+'
    ]

    for p in patterns:
        found = re.findall(p, html)
        for link in found:
            links.add(link.split("?")[0])

    # limit dla stabilności GitHub
    return list(links)[:50]


# --- SPRAWDZENIE OFERTY ---
def check_offer(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None, None

        text = r.text.lower()

        title_match = re.search(r'<title>(.*?)</title>', text)
        title = title_match.group(1) if title_match else ""

        if not valid_book(title):
            return None, None

        price = get_price(text)

        return title, price

    except:
        return None, None


# --- GŁÓWNA LOGIKA ---
state = load_state()
new_state = {}

for search_url in SEARCH_URLS:
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        html = r.text.lower()

        links = extract_links(html)

        for link in links:
            title, price = check_offer(link)

            if not title:
                continue

            new_state[link] = price

            # NOWA OFERTA
            if link not in state:
                notify(f"NOWA OFERTA\n{price} zł\n{link}")

            # ZMIANA CENY
            else:
                old_price = state[link]
                if price and old_price and price != old_price:
                    notify(f"ZMIANA CENY\n{old_price} → {price} zł\n{link}")

            time.sleep(0.7)

    except:
        pass


# --- ZNIKNIĘTE OFERTY ---
for link in state:
    if link not in new_state:
        notify(f"OFERTA ZNIKNĘŁA\n{link}")

save_state(new_state)
