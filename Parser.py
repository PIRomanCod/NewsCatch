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
        # parse_breakinglatest_news:
        #     [
        #         "https://www.breakinglatest.news/news/hall-of-fame-hopes-analyzing-the-pro-football-class-of-2025s-top-contenders-and-controversies/",
        #         "https://www.breakinglatest.news/business/intels-5-billion-vote-of-confidence-strategic-turnaround-or-industry-gamble/",
        #         "https://www.breakinglatest.news/news/hall-of-fame-hopes-analyzing-the-pro-football-class-of-2025s-top-contenders-and-controversies/",
        #         "https://www.breakinglatest.news/news/taylor-swift-takes-a-stand-the-childless-cat-lady-strikes-back-at-political-commentary/",
        #
        #     ],

        # parse_chiswick_calendar:
        #     [
        #         "https://chiswickcalendar.co.uk/hounslow-council-considers-return-to-using-glyphosate-weedkiller/",
        #         "https://chiswickcalendar.co.uk/great-british-elms-mark-seddon-and-david-shreeve-book-review/",
        #         "https://chiswickcalendar.co.uk/belmont-primary-school-want-police-to-protect-their-children/",
        #
        #     ],

        parse_corriere:
            [
                "https://www.corriere.it/oriente-occidente-federico-rampini/24_ottobre_02/gli-usa-e-la-questione-iran-irrisolta-dal-1979-repubblicani-e-democratici-divisi-sull-accordi-con-teheran-8174894d-01e6-4496-8afe-4c4eb00a2xlk.shtml",
                "https://corrieredelveneto.corriere.it/notizie/venezia-mestre/cronaca/24_ottobre_02/filippo-turetta-l-elenco-dei-buoni-propositi-prima-di-uccidere-giulia-cecchettin-apprezzare-la-vita-provare-tinder-andare-a-un-concerto-d6b1055b-e366-4f9a-9eb3-0165b7113xlk.shtml",
                "https://roma.corriere.it/notizie/cronaca/24_ottobre_02/ior-vaticano-licenziati-dipendenti-sposati-ricorso-7aa4aee1-0c0f-454d-89fc-892d8b0e4xlk.shtml",
                "https://www.corriere.it/economia/trasporti/aerei/24_ottobre_02/voli-cancellati-o-in-ritardo-il-boom-delle-agenzie-per-chiedere-i-risarcimenti-con-commissioni-fino-al-50-b3e0c43c-dd94-4ff5-a505-47f36e087xlk.shtml",

            ]
    }

    for parse_function, urls in article_urls.items():
        for url in urls:
            article_data = parse_function(url)
            print(article_data)