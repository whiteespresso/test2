# coding=utf-8
from collections import defaultdict
import random
import scipy
from sklearn import cross_validation
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC, LinearSVC
import datasource
from htmlparser import get_filtered_text, get_link_text_length
import htmlparser


def dict_by_category(entries):
    """
    Zwraca słownik kategoria : lista urli w niej.

    :param entries: lista słowników zawierających url i kategorię
    :returns: słownik kategoria : lista urli w niej
    """
    d = defaultdict(list)
    for entry in entries:
        d[entry['category']].append(entry['url'])
    return d


def get_train_eval_sets(entries, partition):
    """
    Rozdziela zbiór wpisów na zbiór treningowy i testujący.

    :param entries: wpisy: lista słowników zawierających url i kategorię
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :returns: zbiór trenignowy, zbiór testujący
    """
    entrydict = dict_by_category(entries)
    test_set = []
    eval_set = []
    for key in entrydict.iterkeys():
        urls = entrydict[key]
        random.seed(123)
        random.shuffle(urls)
        l = int(round(len(urls) * partition))
        items = [{'category': key, 'url': url} for url in urls]
        test_set.extend(items[:l])
        eval_set.extend(items[l:])

    return test_set, eval_set


def get_trained_classifier(entries):
    """
    Zwraca wytrenowany klasyfikator.

    :param entries: lista słowników zawierających url i kategorię strony
    :returns: wytrenowany klasyfikator
    """
    clf = get_classifier()
    clf.train(entries)
    return clf


def get_classifier():
    """
    Zwraca obiekt klasyfikatora.

    :rtype : CategoryClassifier
    :returns: klasyfikator
    """
    return CategoryClassifier(SGDClassifier())


def get_texts_categories(entry_dict):
    """
    Zwraca słownik z listą przefiltrowanych tekstów stron i ich kategorii.

    :param entry_dict: słownik url: kategoria
    :returns: słownik zawierający listę tekstów i kategorii
    """
    texts = []
    categories = []
    for key in entry_dict:
        text = get_filtered_text(key)
        texts.append(text)
        categories.append(entry_dict[key])

    return {"texts": texts, "categories": categories}


def get_texts_categories_url(entry_dict):
    """
    Zwraca słownik url: text, kategoria

    :param entry_dict:
    :returns: słownik url: text, kategoria
    """
    d = {}
    for key in entry_dict:
        text = get_filtered_text(key)
        d[key] = (text, entry_dict[key])
    return d


def get_menus_categories(entry_dict):
    """
    Zwraca słownik z listą cech menu stron i ich kategorii.

    :param entry_dict: słownik url: kategoria
    :returns: słownik zawierający listę tekstów i kategorii
    """
    texts = []
    categories = []
    for key in entry_dict:
        text = get_menu_features_text(key)
        texts.append(text)
        categories.append(entry_dict[key])

    return {"menus": texts, "categories": categories}


def dict_of_entries(entries):
    """
    Przerabia listę słowników na słownik url:kategoria.

    :param entries: lista słowników zawierających url i kategorię strony
    :returns: słownik url: kategoria
    """
    d = {}
    for e in entries:
        d[e['url']] = e['category']
    return d


def get_count_features(url):
    """
    Dokonuje ekstrakcji cech ilościowych strony.

    :param url: adres strony
    :returns: stosunek tekstu w linkach do tekstu ogółem
    """
    link_length, full_length = get_link_text_length(datasource.get_website(url))
    ratio = link_length / full_length
    if ratio >= 1:
        ratio = 0.99
    return {"ratio": ratio}


def get_menu_features_text(url):
    """
    Zwraca cechy menu strony.

    :param url: adres strony
    :returns: ciąg słów zawartych w menu rozdzielonych spacjami
    """
    return htmlparser.get_menu_features_text(datasource.get_website(url))


class CategoryClassifier(object):
    """
    Klasa odpowiadająca za komunikację z klasyfikatorem i transformowanie cech.
    """

    def __init__(self, skl_clf):
        """
        Konstruktor.

        :param skl_clf: klasyfikator scikit-learn
        """
        self.clf = skl_clf
        self.tfidf_vectorizer = TfidfVectorizer(analyzer="word",
                                                tokenizer=None,
                                                preprocessor=None,
                                                stop_words=None,
                                                max_features=1000)
        self.dict_vectorizer = DictVectorizer()
        self.entry_dict = {}
        self.texts_categories_urls = {}

    def get_texts_categories(self):
        """
        Zwraca listę tekstów i listę kategorii na podstawie słownika będącego zmienną instancyjną klasy.

        :returns: lista tekstów, lista kategorii
        """
        texts = []
        categories = []
        for url in self.texts_categories_urls.iterkeys():
            text = self.texts_categories_urls[url][0]
            category = self.texts_categories_urls[url][1]
            texts.append(text)
            categories.append(category)
        return texts, categories

    def train(self, entries):
        """
        Trenuje klasyfikator.

        :param entries: wpisy - lista słowników zawierających url i kategorię
        :type entries: list[dict[unicode,unicode]]
        """
        entry_dict = dict_of_entries(entries)
        # self.texts_categories = get_texts_categories(self.entry_dict)
        self.texts_categories_urls.update(get_texts_categories_url(entry_dict))
        texts, categories = self.get_texts_categories()
        feature_vec = self.tfidf_vectorizer.fit_transform(texts)

        self.clf.fit(feature_vec, categories)

    def classify(self, url):
        """
        Klasyfikuje stronę.

        :param url: adres strony
        :type url: unicode
        :returns: wynik klasyfikacji
        """
        features = get_filtered_text(url)
        feature_vec = self.tfidf_vectorizer.transform([features])

        return self.clf.predict(feature_vec)[0]

    def accuracy(self, eval_entries):
        """
        Liczy stosunek poprawnie sklasyfikowanych stron do pełnej liczby stron w zbiorze testowym.

        :param eval_entries: zbiór testowy - lista słowników zawierających url i kategorię
        :type eval_entries: list[dict[unicode,unicode]]
        :returns: stosunek poprawnie sklasyfikowanych stron do pełnej liczby stron w zbiorze testowym
        """
        gold = [entry['category'] for entry in eval_entries]

        predicted = [self.classify(entry['url'])
                     for entry in eval_entries]
        correct = [l == r for l, r in zip(gold, predicted)]
        wrong = []
        for predict, entry in zip(predicted, eval_entries):
            if predict != entry['category']:
                wrong.append(" ".join([entry['url'], predict]))
        print wrong
        if correct:
            return float(sum(correct)) / len(correct)
        else:
            return 0

    def xval(self, entries, folds):
        """
        Liczy walidację krzyżowa stratyfikowaną.

        :param entries: wpisy
        :param folds: liczba podzbiorów na które zostanie podzielony zbiór wpisów
        :returns: wynik walidacji krzyżowej
        """
        entry_dict = dict_of_entries(entries)
        texts_categories = get_texts_categories(entry_dict)
        # menus_categories = get_menus_categories(entry_dict)
        texts = texts_categories["texts"]
        # menus = menus_categories["menus"]
        # categories = menus_categories["categories"]
        categories = texts_categories["categories"]
        feature_vec = self.tfidf_vectorizer.fit_transform(texts)
        # menu_vec = self.tfidf_vectorizer.fit_transform(menus)
        # len_features = list(map(get_count_features, entry_dict.iterkeys()))
        # len_features = map(get_count_features, entry_dict.iterkeys())
        # len_features = map(get_contains_features, entry_dict.iterkeys())
        # len_vec = self.dict_vectorizer.fit_transform(len_features)

        # full_vec = scipy.sparse.hstack([feature_vec, menu_vec])

        score = cross_validation.cross_val_score(self.clf, feature_vec, categories, cv=folds)
        return score, sum(score)/len(score)
