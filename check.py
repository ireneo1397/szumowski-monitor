import requests
import hashlib
import os
import time

TOPIC = "szumowski-alert"
STATE_FILE = "state.txt"

# POLSKIE SERWISY (tylko)
URLS = [
    # Allegro kup teraz
    "https://allegro.pl/listing?string=szumowski+dooko%C5%82a+%C5%9Bwiata",

    # Allegro licytacje
    "https://allegro.pl/listing?string=szumowski+dooko%C5%82a+%C5%9Bwiata&offerTypeAuction=1",

    # Allegro Lokalnie
    "https://allegrolokalnie.pl/oferty/q-szumowski-dookola-swiata",

    # OLX
    "https://www.olx.pl/oferty/q-szumowski-dookola-swiata/",

    # Vinted PL
    "https://www.vinted.pl/catalog?search_text=szumowski+dookola+swiata",

    # Sprzedajemy
    "https://sprzedajemy.pl/szukaj?query=szumowski+dookola+swiata",

    # Gratka
    "https://gratka.pl/szukaj?query=szumowski+dookola+swiata",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# SZUKANE FRAZY (różne warianty nazwy)
KEYWORDS = [
    "szumowski",
    "dookoła świata",
    "dookola swiata",
    "komik dookoła świata",
    "komik dookola swiata"
]

# FRAZY DO WYKLUCZENIA (część 2 – czerwona)
EXCLUDE = [
    "część 2",
    "czesc 2",
    "tom 2",
    "część druga",
    "czesc druga",
    "2"
]


def notify(message):
    try:
        requests.post(
            f"https://ntfy.sh/{TOPIC}",
            data=message.encode("utf-8"),
            timeout=10
        )
    except:
        pass


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        for item in state:
            f.write(item + "\n")


def get_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def valid_offer(text):
    text = text.lower()

    # musi zawierać słowa kluczowe
    if not any(k in text for k in KEYWORDS):
        return False

    # nie może zawierać informacji o części 2
    if any(e in text for e in EXCLUDE):
        return False

    return True


def check_urls():
    state = load_state()
    new_state = set(state)

    for url in URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)

            # sprawdzenie czy strona działa
            if r.status_code != 200:
                continue

            text = r.text.lower()

            # sprawdzenie czy to właściwa książka (część 1)
            if not valid_offer(text):
                continue

            # hash strony (wykrywa zmiany ceny/opisu)
            page_hash = get_hash(text[:5000])  # tylko fragment – szybciej

            key = f"{url}|{page_hash}"

            if key not in state:
                message = f"NOWA lub ZMIENIONA oferta:\n{url}"

                # informacja o licytacji
                if "auction" in url or "licytac" in text:
                    message += "\n(Uwaga: możliwa licytacja)"

                notify(message)
                new_state.add(key)

        except:
            # błąd strony – pomijamy
            continue

        time.sleep(2)  # żeby nie blokowali

    save_state(new_state)


if __name__ == "__main__":
    check_urls()
