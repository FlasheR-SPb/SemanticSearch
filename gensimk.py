# -*- coding: utf-8 -*-
__author__ = 'FlasheR'

# РАБОТАЮЩИЙ КОД РЕАЛИЗОВАН В TEST.PY

from gensim import corpora, models, similarities
import cleaner
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
news = []

file = open('news.txt')
for line in file:
    news.append(file.readline())


# # НЕ ДОДЕЛАН: cleaner.Porter.stem(word) из-за ошибки AttributeError: 'NoneType' object has no attribute
# texts = [[word for word in document.lower().split() if word not in cleaner.stops]
#          for document in news]


# собирает статистические данные обо всех маркерах
dictionary = corpora.Dictionary(word for word in line.lower().split() for line in open('news.txt'))
print(dictionary)
# удаляет слова и слова повторяющиеся однажды
stop_ids = [dictionary.token2id[stopword] for stopword in cleaner.stops
            if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq == 1]
dictionary.filter_tokens(stop_ids + once_ids) # удаляет слова и слова повторяющиеся однажды
dictionary.compactify() # удаляет пробелы в поледовательности идентификаторов, после чистки

# сохраняем словарь для дальнейшего использования
dictionary.save('deerwester.dict')

#  Корпусная потоковая передача – один документ за раз
class MyCorpus(object):
    def __iter__(self):
        for line in open('news.txt'):
            # предположим, что есть один документ в строке, лексемы разделяются пробелами
            yield dictionary.doc2bow(line.lower().split())

corpus_memory_friendly = MyCorpus() # не загружает корпус в память

corpora.MmCorpus.serialize('corpus.mm', corpus_memory_friendly)

dictionary = corpora.Dictionary.load('deerwester.dict')
corpus = corpora.MmCorpus('corpus.mm')


tfidf = models.TfidfModel(corpus) # шаг 1 - инициализация модели
corpus_tfidf = tfidf[corpus]
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # инициализация LSI преобразования
corpus_lsi = lsi[corpus_tfidf] # создание двойной обертки поверх оригинального корпуса: bow->tfidf->fold-in-lsi

doc = "футбол" # тренер, футболист, трансферное, мяч
vec_bow = dictionary.doc2bow(doc.lower().split())
vec_lsi = lsi[vec_bow] # преобразование запроса к LSI пространству

print("Vec_LSI:")
print(vec_lsi)

index = similarities.MatrixSimilarity(lsi[corpus])

sims = index[vec_lsi] # запрос подобия по отношению к корпусу

sims = sorted(enumerate(sims), key=lambda item: -item[1])
print("Sims:")
print(sims)
