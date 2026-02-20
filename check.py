import requests
import hashlib
import os

TOPIC = "szumowski-alert"

URLS = {
    # główne
    "allegro": "https://allegro.pl/listing?string=komik%20dookoła%20świata%20szumowski",
    "allegro_lokalnie": "https://allegrolokalnie.pl/oferty/q-komik-dookoła-świata-szumowski",
    "olx": "https://www.olx.pl/oferty/q-komik-dookoła-świata-szumowski/",
    "vinted": "https://www.vinted.pl/catalog?search_text=komik+dookoła+świata+szumowski",

    # ogłoszeniowe
    "sprzedajemy": "https://sprzedajemy.pl/szukaj?query=komik%20dookoła%20świata%20szumowski",
    "gratka": "https://gratka.pl/szukaj?query=komik%20dookoła%20świata%20szumowski",
    "lento": "https://lento.pl/szukaj.html?q=komik+dookoła+świata+szumowski",

    # sklepy / porównywarki
    "empik": "https://www.empik.com/szukaj/produkt?query=komik%20dookoła%20świata%20szumowski",
    "ceneo": "https://www.ceneo.pl/;szukaj-komik+dookoła+świata+szumowski",
    "skapiec": "https://www.skapiec.pl/szukaj/w_calym_serwisie/komik+dookoła+świata+szumowski",

    # agregator
    "google": "https://www.google.com/search?q=komik+dookoła+świata+szumowski+sprzedam"
}

STATE_FILE = "state.txt"

def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

old_state = {}

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        for line in f:
            name, h = line.strip().split("|")
            old_state[name] = h

new_state = {}

headers = {
    "User-Agent": "Mozilla/5.0"
}

for name, url in URLS.items():
    try:
        r = requests.get(url, headers=headers, timeout=15)
        text = r.text.lower()
        fragment = text[:60000]
        h = get_hash(fragment)
        new_state[name] = h

        if name not in old_state:
            notify(f"Start monitorowania: {name}")

        elif old_state[name] != h:
            notify(f"Nowa oferta!\n{name}\n{url}")

    except:
        pass

with open(STATE_FILE, "w") as f:
    for name, h in new_state.items():
        f.write(f"{name}|{h}\n")
