# -*- coding: utf-8 -*-
__author__ = 'FlasheR'

import urllib.request
from bs4 import BeautifulSoup
import csv

SPORT = "http://bombardir.ru"
footballNewsList = list()

def get_links(base_url):
    html = urllib.request.urlopen(base_url).read()
    soup = BeautifulSoup(html, "html.parser")
    span = soup.find_all('span', class_='soc-text')
    links = list()
    for a in span:
        links.append(a.find('a').get('href').strip())

    return links

def parse(url):
    html = urllib.request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find('div', class_='content').text.strip().split()
    title = soup.find('h1', class_='content-headline').text.strip().split()
    div1 = ' '.join(str(e) for e in div)
    title1 = ' '.join(str(e) for e in title)

    article = []

    article.append({'title': title1, 'text': div1})

    return article

def save(news, path):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow('Текст')

        writer.writerows(
            (''.join(new['text'])) for new in news
        )

def main():
    footballNewsList = get_links(SPORT + '/news')
    news_count = len(footballNewsList)

    all_news = []

    print("News:",news_count)
    for news in range(0, news_count):
        print("Parse %d%%" %(news / news_count * 100))
        all_news.extend(parse(SPORT + footballNewsList[news]))

    for news in all_news:
        print(news)

    # save(all_news, 'projects.csv')

    f = open('news.txt', 'w')
    for new in all_news:
        f.write(new['text'] + '\n')

if __name__ == '__main__':
    main()

