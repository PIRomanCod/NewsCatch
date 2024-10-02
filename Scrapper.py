from multiprocessing import Process

import scrapy
from scrapy.crawler import CrawlerProcess


class ISpider(scrapy.Spider):
    """Base class for all spiders."""
    pass


class INewsCoUkSpider(ISpider):
    """Spider for inews.co.uk website."""
    name = "inews_co_uk"
    allowed_domains = ["inews.co.uk"]
    start_urls = ["https://inews.co.uk/category/news/"]
    custom_settings = {
        "FEED_FORMAT": "json",
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_URI": f"inews_co_uk.json"
    }

    def parse(self, response):
        """Parse the main page."""
        category_links = response.css(".inews__sub__header_menu_list_item::attr(href)").extract()
        for category_link in category_links:
            yield scrapy.Request(url=category_link, callback=self.parse_item)

    def parse_item(self, response):
        """Parse individual news items."""
        known_selectors = {
            "science": ".inews__post-section__body .inews__post",
            "housing": ".inews__post.inews__post-teaser.opinion"
        }

        category_url = response.url

        news_selector = next((selector for category, selector in known_selectors.items() if category in category_url),
                             None)

        if news_selector:
            content = response.css(news_selector + " a::attr(href)").extract()
        else:
            content = response.css(".inews__post-jot__content a::attr(href)").extract()

        news_links = set(link for link in content if "-" in link and not "author" in link)

        for link in news_links:
            yield {
                "base_url": response.url,
                "url": link,
            }


class SvtSeSpider(ISpider):
    """Spider for svt.se website."""
    name = "svt_se"
    allowed_domains = ["svt.se"]
    start_urls = ["https://www.svt.se/"]
    custom_settings = {
        "FEED_FORMAT": "json",
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_URI": f"svt_se.json"
    }

    def parse(self, response):
        """Parse the main page."""
        category_links = ["ekonomi/", "nyhetstecken/", "uutiset/", "svtforum/", "sapmi/",
                          "vetenskap/", "granskning/", "om/svt-nyheter-verifierar/", "vader/",
                          "inrikes/", "kultur/", "utrikes/"]
        for category_link in category_links:
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_item)

    def parse_item(self, response):
        """Parse individual news items."""
        news_links = response.css(".nyh_teaser__link::attr(href)").extract()

        for news_link in news_links:
            absolute_news_link = response.urljoin(news_link)
            yield {
                "base_url": response.url,
                "url": absolute_news_link,
            }


class RtpPtSpider(ISpider):
    """Spider for rtp.pt website."""
    name = "rpt_pt"
    allowed_domains = ["www.rtp.pt"]
    start_urls = ["https://www.rtp.pt/noticias/pais", "https://www.rtp.pt/noticias/mundo",
                  "https://www.rtp.pt/noticias/politica", "https://www.rtp.pt/noticias/economia",
                  "https://www.rtp.pt/noticias/cultura", "https://www.rtp.pt/noticias/desporto"]
    custom_settings = {
        "FEED_FORMAT": "json",
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_URI": f"rpt_pt.json",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

    }

    def parse(self, response):
        """Parse the main page."""
        category_links = response.css("ul.navbar-nav a.nav-link::attr(href)").extract()
        for category_link in category_links:
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_item)

    def parse_item(self, response):
        """Parse individual news items."""
        content = response.css(".tab-content ::attr(href)").extract()

        news_links = set(link for link in content if "-" in link and not "antena1" in link and not "cdn-images" in link)

        for link in news_links:
            yield {
                "base_url": response.url,
                "url": link,
            }


class RtbfBESpider(ISpider):
    """Spider for rtbf.be website."""
    name = "rtbf_be"
    allowed_domains = ["rtbf.be"]
    start_urls = ["https://www.rtbf.be"]
    custom_settings = {
        "FEED_FORMAT": "json",
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_URI": f"rtbf_be.json",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

    }

    def parse(self, response):
        """Parse the main page."""
        category_links = ["/en-continu", "/info", "/dossier/elections-2024", "/sport", "/regions",
                          "/culture/", "/environnement/", "/bien-etre", "/tech", "/vie-pratique", "/emissions"]
        for category_link in category_links:
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_item)

    def parse_item(self, response):
        """Parse individual news items."""
        content = response.css(".stretched-link::attr(href)").getall()
        news_links = set(link for link in content if "-" in link and not "antena1" in link and not "cdn-images" in link)
        for link in news_links:
            absolute_news_link = response.urljoin(link)
            yield {
                "base_url": response.url,
                "url": absolute_news_link,
            }


def run_spider(entity: ISpider):
    """Run the spider."""
    process = CrawlerProcess()
    process.crawl(entity)
    process.start()


if __name__ == "__main__":
    spider_classes = [INewsCoUkSpider, SvtSeSpider, RtpPtSpider, RtbfBESpider]

    processes = []
    try:
        for spider_class in spider_classes:
            process = Process(target=run_spider, args=(spider_class,))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
