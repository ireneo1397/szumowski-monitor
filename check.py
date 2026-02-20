import requests
import os

TOPIC = "szumowski-alert"

# Plik z zapamiętanymi ofertami
SEEN_FILE = "seen.txt"

# Wczytaj zapisane linki
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_links = set(f.read().splitlines())
else:
    seen_links = set()

# Wszystkie serwisy (w tym licytacje Allegro)
URLS = [
    # Allegro - kup teraz
    "https://allegro.pl/listing?string=szumowski%20dooko%C5%82a%20%C5%9Bwiata",

    # Allegro - tylko aukcje (licytacje)
    "https://allegro.pl/listing?string=szumowski%20dooko%C5%82a%20%C5%9Bwiata&offerTypeAuction=1",

    # OLX
    "https://www.olx.pl/oferty/q-szumowski-dooko%C5%82a-%C5%9Bwiata/",

    # Allegro Lokalnie
    "https://allegrolokalnie.pl/oferty/q-szumowski-dookola-swiata",

    # Vinted
    "https://www.vinted.pl/catalog?search_text=szumowski+dookoła+świata"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))

new_links = set()

for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            continue

        text = r.text.lower()

        # Szukaj linków do ofert
        parts = text.split('href="')

        for part in parts:
            if part.startswith("https"):
                link = part.split('"')[0]

                # Filtr: musi zawierać szumowski
                if "szumowski" in link:

                    # Jeśli nowy link
                    if link not in seen_links:
                        new_links.add(link)

                        # Sprawdź czy aktywny
                        try:
                            test = requests.get(link, headers=HEADERS, timeout=10)
                            if test.status_code == 200:
                                notify(f"Nowa oferta lub licytacja:\n{link}")
                        except:
                            pass

    except:
        pass

# Zapisz nowe linki
if new_links:
    with open(SEEN_FILE, "a") as f:
        for link in new_links:
            f.write(link + "\n")
