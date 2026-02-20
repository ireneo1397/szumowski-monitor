import requests

TOPIC = "szumowski-alert"

URLS = [
    "https://allegro.pl/listing?string=komik%20dookoła%20świata%20szumowski",
    "https://www.olx.pl/oferty/q-komik-dookoła-świata-szumowski/",
    "https://allegrolokalnie.pl/oferty/q-komik-dookoła-świata-szumowski"
]

def notify(message):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"))

for url in URLS:
    try:
        r = requests.get(url, timeout=10)
        text = r.text.lower()
        if "szumowski" in text and "komik" in text:
            notify(f"Możliwa oferta:\n{url}")
    except:
        pass
