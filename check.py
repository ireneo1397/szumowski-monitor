def is_valid_offer(text, url):
    t = text.lower()

    # Musi zawierać książkę
    required = [
        "komik",
        "dookoła",
        "szumowski"
    ]

    if not all(word in t for word in required):
        return False

    # ODRZUĆ część 2
    part2_words = [
        "świata 2",
        "dookola świata 2",
        "część 2",
        "czesc 2",
        "tom 2",
        "vol 2"
    ]

    if any(word in t for word in part2_words):
        return False

    # ODRZUĆ profile użytkowników
    bad_url_parts = [
        "/member",
        "/profile",
        "/user"
    ]

    if any(part in url.lower() for part in bad_url_parts):
        return False

    return True
