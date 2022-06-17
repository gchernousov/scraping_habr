import requests
from bs4 import BeautifulSoup

import re
from tqdm import tqdm
from pprint import pprint as pp


KEYWORDS = ['дизайн', 'фото', 'web', 'python']

MAIN_URL = "https://habr.com/ru/all/"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                        "application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "habr.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


def connect():
    """Подключение к habr.com"""
    res = requests.get(MAIN_URL, headers=HEADERS)
    if res.status_code == 200:
        return res
    else:
        print("!!! Connection Error !!!")


def get_all_articles(html):
    """Получение всех свежих статей с главной страницы"""
    soup = BeautifulSoup(html.text, "html.parser")
    articles = soup.find_all("div", class_="tm-article-snippet")

    return articles


def get_article_url(article):
    """Получение ссылки на статью"""
    habr_url = "https://habr.com"

    url = article.find("a", class_="tm-article-snippet__title-link").get("href")
    url = f"{habr_url}{url}"

    return url


def get_article_text(article):
    """Получение текста статьи"""
    url = get_article_url(article)

    html = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    article_body = soup.find("div", id="post-content-body").find_all("p")
    article_text = ""
    for p in article_body:
        article_text += p.text

    return article_text


def gen_article_info(article):
    """Формирование информации о статье: дата создания, заголовок, ссылка"""
    article_url = get_article_url(article)

    html = requests.get(article_url, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    article_body = soup.find("article", class_="tm-article-presenter__content")

    article_date = article_body.find("time").get("title")
    article_title = article_body.find("h1", class_="tm-article-snippet__title").find("span").text

    article_info = {
        "date": article_date,
        "title": article_title,
        "url": article_url
    }

    return article_info


def collect_needful_articles(articles_list):
    """Сбор нужных статей по ключевым словам"""
    result_articles = []

    for article in tqdm(articles_list):
        article_text = get_article_text(article)
        result_keywords = []

        for word in KEYWORDS:
            pattern = f"[{word[0].capitalize()}|{word[0]}]{word[1:]}[а-я]*"
            result = re.findall(pattern, article_text)
            result_keywords.append(result)

        result_keywords_oneline = []
        for keyword in result_keywords:
            result_keywords_oneline += [*keyword]

        if len(result_keywords_oneline) >= 1:
            article_info = gen_article_info(article)
            result_articles.append(article_info)

    return result_articles

if __name__ == "__main__":

    print(f"Поиск статей с ключевыми словами: {', '.join(KEYWORDS)}\n")
    html = connect()
    articles = get_all_articles(html)
    result_articles = collect_needful_articles(articles)
    print(f"\nНайденно {len(result_articles)} статей:\n")
    pp(result_articles)