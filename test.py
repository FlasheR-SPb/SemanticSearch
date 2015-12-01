# -*- coding: utf-8 -*-
__author__ = 'FlasheR'

from gensim import corpora, models, similarities
import cleaner
import pymorphy2
import re
from collections import defaultdict
from pprint import pprint   # pretty-printer

morph = pymorphy2.MorphAnalyzer()

documents = []

# file = open('news.txt')
# for line in file:
#     documents.append(file.readline())

i = 0
while i < 8:
    fileName = str(i) + ".txt"
    file = open("resources/" + fileName)
    documents.append(file.readline())
    i += 1

texts = []
for document in documents:
    sublist = []
    for word in document.lower().split():
        word = re.sub(r'[;,\—\–\-\(\).\s\d:"]', '', word)
        if (word != '' and word not in cleaner.stops):
            sublist.append(morph.parse(word)[0].normal_form)
    texts.append(sublist)


# удаляем слова, встречающиеся единожды
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1]
         for text in texts]

# для просмотра списка списков, теперь необходимо использовать pretty-printer, раскомментировать
pprint(texts)

# реализация словаря
dictionary = corpora.Dictionary(texts)

# сохраняем словарь для дальнейшего использования
dictionary.save('deerwester.dict')

# создаем корпус и сериализуем его
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('corpus.mm', corpus)


tfidf = models.TfidfModel(corpus) # шаг 1 - инициализация модели tfidf
corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # инициализация LSI трансформации
corpus_lsi = lsi[corpus_tfidf] # создание двойной оболочки поверх оригинального корпуса: bow->tfidf->fold-in-lsi

# реализация поиска
doc = "птица"
vec_bow = dictionary.doc2bow(doc.lower().split())
vec_lsi = lsi[vec_bow] # преобразование запроса к LSI пространству

index = similarities.MatrixSimilarity(lsi[corpus])

sims = index[vec_lsi] # запрос подобия по отношению к корпусу

sims = sorted(enumerate(sims), key=lambda item: -item[1])
print("Sims:")
print(sims)

# Тесты
# Для тестов выбраны 7 файлов: 0-3 про футбол, 4-5 про птиц разных видов, 6-ой косвенно пересекается со 4-м, 7 - абсолютно левая тематика
# Ключевые слова на взгляд:
# 0: реал, футболист, команда, травма, примера,
# 1: реал, чемпионат, Барселона, полузащитник
# 2: полузащитник, зенит
# 3: Зенит, Барселона, футболист
# 4: попугай, птица, клюв, хвост, зеленый
# 5: клюв, птица (?)                              - не указано слово птица, но документ должен попадать в запрос
# 6: яблоко, зеленый                              - документ имеет мало ключевых слов, но если мы интересуемся зеленым, то точно должны видеть этот документ
# 7: душа, понятие, вопрос, тело,                 - файл сложен для парсинга, больше нужен как тестер морфия и клинера, а так же роли "белой вороны"
# Слова для поиска: реал, футболист, команда, барселона, зенит, полузащитник, примера(?), чемпионат(?), попугай, птица(?), клюв, зеленый, душа, тело, вопрос

