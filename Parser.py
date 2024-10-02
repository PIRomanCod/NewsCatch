import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def parse_24heures_news(url):
    """
    Parses articles from the 24heures website.
    Args:
        url (str): The URL of the article.
    Returns:
        dict: A dictionary containing the parsed data including title, content, author, and date.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("span", class_="ContentHead_text__2MEnX").text.strip()

        content_tags = soup.find_all("span", class_="HtmlText_root__A1OSq")

        content = ""
        for tag in content_tags:
            content += tag.get_text(strip=True) + " "

        content = content.strip()
        symbols_to_replace = ["\xa0", "\u2009"]
        for symbol in symbols_to_replace:
            content = content.replace(symbol, " ")

        author_tag = soup.find("span", class_="ContentMetaInfo_author__6_Vnu")
        author = author_tag.text.strip() if author_tag else None
        if not author:
            author_tag = soup.find("div", class_="ContentCaption_contentcredit__zUOv5 ContentCaption_width__xf6My")
            author = author_tag.text.strip().split("/")[-1] if author_tag else None

        date_tag = soup.find("time", class_="FullDateTime_root__K7FL2")
        if date_tag:
            date_string = date_tag["datetime"]
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

        news = {"title": title, "content": content, "author": author, "date": date}

        return news
    else:
        print(f"Failed to fetch article from {url}")
        return None


def parse_breakinglatest_news(url):
    """
    Parses articles from the Breaking Latest website.
    Args:
        url (str): The URL of the article.
    Returns:
        dict: A dictionary containing the parsed data including title, content, author, and date.
    """
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch article from {url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("h1", class_="post-title single-post-title entry-title").text.strip()

    content_tags = soup.find_all("div", class_="inner-post-entry entry-content")
    content = ""
    for tag in content_tags:
        relevant_tags = tag.find_all("p", recursive=False)
        for relevant_tag in relevant_tags:
            class_list = relevant_tag.get("class", [])
            text = relevant_tag.get_text(strip=True)
            if all([
                "hbvl-ebe0ecc6_caption2" not in class_list,
                "(Read more below the post)" not in text,
                "Read also:" not in text,
                "News on" not in text,
                "Loading player" not in text,
                "I like" not in text,
                "pgallery-info" not in class_list,
                "View" not in text,
                "is-copyright" not in class_list,
                "wp-caption-text" not in class_list,
                "Email Share" not in text,
                "Spotted an Error?" not in text,
                "Please mark the relevant words" not in text,
                "Links marked with a symbol" not in text,
                "(advertisement)" not in text,
                "noads" not in class_list,
                not relevant_tag.find("strong", string="READ ALSO")
            ]):
                content += text + " "
    if not content:
        content_tags = soup.find_all("p")
        for content_tag in content_tags:
            class_list = content_tag.get("class", [])
            text = content_tag.get_text(strip=True)
            if all([
                "comment-form-cookies-consent" not in class_list,
                "akismet_comment_form_privacy_notice" not in class_list,
                "Hosted" not in text,
                "This website uses" not in text,
                "is-copyright" not in class_list,
            ]):
                content += text + " "

    symbols_to_replace = ["\xa0", "\u2009", "Δ", "\u200b"]
    for symbol in symbols_to_replace:
        content = content.replace(symbol, " ")
    content = content.strip()

    author_tag = soup.find("span", class_="ContentMetaInfo_author__6_Vnu")
    author = author_tag.text.strip() if author_tag else None
    if not author:
        author_tag = soup.find("div", class_="ContentCaption_contentcredit__zUOv5 ContentCaption_width__xf6My")
        author = author_tag.text.strip().split("/")[-1] if author_tag else None

    date_tag = soup.find("time", class_="entry-date published")
    if date_tag:
        date_string = date_tag["datetime"]
        date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
        date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    news = {"title": title, "content": content, "author": author, "date": date}

    return news


def parse_chiswick_calendar(url):
    """
    Parses articles from the Chiswick Calendar website.
    Args:
        url (str): The URL of the article.
    Returns:
        dict: A dictionary containing the parsed data including title, content, author, and date.
    """
    request_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=request_headers)

    if response.status_code != 200:
        print(f"Failed to fetch article from {url}")
        print(f"Error message: {response.text}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("h1", class_="post-title entry-title").text.strip()

    content_tags = soup.find_all("div", class_="entry-content")
    content = ""
    for tag in content_tags:
        relevant_tags = tag.find_all("p", recursive=False)
        for relevant_tag in relevant_tags:
            class_list = relevant_tag.get("class", [])
            text = relevant_tag.get_text(strip=True)
            if all([
                "comment" not in class_list,
                "post-meta" not in class_list,
                "entry-meta" not in class_list,
                "social" not in class_list,
                "More Stories" not in text,
                not relevant_tag.find("em"),
                "Read more" not in text,
            ]):
                content += text + " "

    symbols_to_replace = ["\xa0", "\u2009", "Δ", "\u200b"]
    for symbol in symbols_to_replace:
        content = content.replace(symbol, " ")
    content = content.strip()

    author_tag = soup.find("span", class_="author")
    author = author_tag.text.strip() if author_tag else None

    date_tag = soup.find("time", class_="date-container minor-meta updated")
    if date_tag:
        date_string = date_tag["datetime"]
        date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
        date = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    news = {"title": title, "content": content, "author": author, "date": date}

    return news


def parse_corriere(url):
    """
    Parses articles from the Corriere website.
    Args:
        url (str): The URL of the article.
    Returns:
        dict: A dictionary containing the parsed data including title, content, author, and date.
    """
    request_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=request_headers)

    if response.status_code != 200:
        print(f"Failed to fetch article from {url}")
        print(f"Error message: {response.text}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("h1", class_="title-art-hp")
    if not title:
        title = soup.find("h1", class_="title")
    if not title:
        title = soup.find("h1", class_="title-art")
    title = title.text.strip()

    content_tags = soup.find_all(["p", "div"], class_={"content", "chapter-paragraph", "paragraph"})
    content = ""
    for tag in content_tags:
        relevant_tags = tag.find_all(["p", "i", "div", "figcaption", "figure"], recursive=False)
        for relevant_tag in relevant_tags:
            class_list = relevant_tag.get("class", [])
            text = relevant_tag.get_text(strip=True)
            if all([
                "bck-media-list" not in class_list,
                "bck-media-news" not in class_list,
                "is-copyright" not in class_list,
                not relevant_tag.name == "bck-media-list",
                not relevant_tag.name == "bck-media-news",
                not relevant_tag.name == "figcaption",
                not relevant_tag.name == "figure",
                "Corriere della Sera" not in text,
                "È sufficiente" not in text,
                "Whatsapp" not in text,
                "Vai a tutte le notizie" not in text,
                "Se vuoi restare aggiornato sulle notizie" not in text,
                "RIPRODUZIONE RISERVATA" not in text,
                "Basta" not in text,

            ]):
                content += text + " "

    symbols_to_replace = ["\xa0", "\u2009", "Δ", "\u200b", "lferrarella@corriere.it"]
    for symbol in symbols_to_replace:
        content = content.replace(symbol, " ")
    content = content.strip()

    author_tag = soup.find("span", class_="writer")
    author = author_tag.text.strip() if author_tag else None

    date_tags = soup.find_all(["div", "p"], class_="is-last-update")
    date = None
    for tag in date_tags:
        datetime_attr = tag.get("datetime")
        content_attr = tag.get("content")
        if datetime_attr:
            date = datetime_attr.strip()
            break
        elif content_attr:
            date = content_attr.strip()
            break
    if not date:
        date_tag = soup.find("meta", attrs={"name": "DC.date.issued", "content": re.compile(r'\d{4}-\d{2}-\d{2}')})
        date = date_tag["content"] if date_tag else None

    news = {"title": title, "content": content, "author": author, "date": date}

    return news


if __name__ == "__main__":
    article_urls = {
        parse_24heures_news:
            [
                "https://www.24heures.ch/crime-des-monts-de-corsier-la-condamnee-saisit-le-tf-339847387171",
                "https://www.24heures.ch/linitiative-sur-la-neutralite-recolte-132780-signatures-315228781097",
                "https://www.24heures.ch/gens-du-voyage-une-partie-des-gitans-a-quitte-yverdon-pour-morrens-956418978102",
                "https://www.24heures.ch/morges-le-quartier-eglantine-ne-sera-securise-quen-2026-311821555953",
                "https://www.24heures.ch/tour-de-romandie-des-perturbations-sur-les-routes-vaudoises-711758956582",
                "https://www.24heures.ch/editorial-tout-un-canton-vibre-de-nouveau-pour-le-lhc-644187193751",
            ],
        parse_breakinglatest_news:
            [
                "https://www.breakinglatest.news/world/operation-praetorian-mp-requests-preventive-detention-for-madureira-and-polaco-public-ministry-2041/",
                "https://www.breakinglatest.news/news/sharing-open-opportunities-and-creating-a-better-life-together-written-on-the-occasion-of-the-upcoming-opening-of-the-4th-consumer-expo-xinhuanet-client/",
                "https://www.breakinglatest.news/entertainment/well-known-harry-potter-bridge-will-soon-be-renovated-we-respect-its-historical-significance/",
                "https://www.breakinglatest.news/health/reflux-many-false-myths-about-taboo-foods-gastroenterology/",
                "https://www.breakinglatest.news/news/pnc-guarantees-security-and-prevention-of-violence-in-schools/",
                "https://www.breakinglatest.news/entertainment/the-mysteries-of-the-etoile-bar-a-tragicomedy-that-works-halfway/",
                "https://www.breakinglatest.news/technology/apple-app-store-backend-bug-shows-developers-millions-of-dollars-in-revenue-2/",
                "https://www.breakinglatest.news/world/udinese-news-the-first-news-on-thauvin-heres-when-he-will-return/",
                "https://www.breakinglatest.news/sports/the-green-jacket-that-all-golfers-want/",
                "https://www.breakinglatest.news/health/new-large-scale-study-reveals-surprising-health-effects-of-garlic/",
                "https://www.breakinglatest.news/business/imf-on-ecb-day-the-inflation-rate-warning-to-central-banks-dont-be-in-a-hurry-to-cut/",

            ],

        parse_chiswick_calendar:
            [
                "https://chiswickcalendar.co.uk/2024-sw-london-assembly-elections-interview-with-liberal-democrat-candidate-gareth-roberts/",
                "https://chiswickcalendar.co.uk/thames-tradesmen-win-bronze-at-masters-head-of-the-river-race/",
                "https://chiswickcalendar.co.uk/the-old-pack-horse-reopens-after-refurbishment/",
                "https://chiswickcalendar.co.uk/cache-of-paintings-of-chiswick-found-painted-by-once-celebrated-artist-heather-jenkins/",
                "https://chiswickcalendar.co.uk/iran-international-journalist-stabbed-outside-london-home/",

            ],

        parse_corriere:
            [
                "https://www.corriere.it/esteri/24_aprile_08/zaporizhzhia-esperti-copertura-centrale-puo-resistere-a-impatto-aereo-73c57a44-f5e5-11ee-82ba-27cf75319ae5.shtml",
                "https://milano.corriere.it/notizie/cronaca/24_aprile_12/daniela-santanche-seconda-accusa-dei-pm-alla-ministra-del-turismo-ha-falsificato-i-bilanci-di-visibilia-1fe55b28-336a-404c-a33d-103dd7fcfxlk.shtml",
                "https://www.corriere.it/sport/24_aprile_12/kate-antropova-volley-paola-egonu-intervista-67a115b6-f833-11ee-95a0-2c72581cb5a3.shtml",
                "https://roma.corriere.it/notizie/politica/24_aprile_12/diffamazione-blitz-di-fdi-si-al-carcere-per-i-giornalisti-ma-il-centrodestra-si-spacca-45d7386d-07ad-499e-b4ae-1e02be5e5xlk.shtml",
                "https://www.corriere.it/economia/finanza/24_aprile_12/argento-e-oro-ai-massimi-cosa-succede-alle-quotazioni-dei-metalli-preziosi-4fcc7a59-1015-47f6-9ecd-ffc662c2cxlk.shtml",
                "https://www.corriere.it/salute/pediatria/24_aprile_12/mal-di-testa-negli-adolescenti-quali-possono-essere-le-cause-e-come-intervenire-d00c2f4d-fd37-4d1b-b199-0e220455fxlk.shtml",
                "https://www.corriere.it/esteri/24_aprile_11/famiglia-haniyeh-figli-martiri-quelli-con-lui-esilio-dorato-qatar-8339d3a8-f7e8-11ee-95a0-2c72581cb5a3.shtml",
                "https://www.corriere.it/sport/tennis/cards/chi-holger-rune-avversario-sinner-montecarlo/nuova-sfida-rune-sinner_principale.shtml",
                "https://www.corriere.it/economia/finanza/24_aprile_11/bce-tassi-invariati-4-50-ma-si-prepara-il-taglio-con-piu-certezze-sull-inflazione-50f16a1a-92ca-45e9-b0b2-a50958367xlk.shtml",

            ]
    }

    for parse_function, urls in article_urls.items():
        for url in urls:
            article_data = parse_function(url)
            print(article_data)