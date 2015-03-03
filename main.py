# coding=utf-8
import cPickle as pickle
import random

import classifier
import datasource


def classify_website(url, filename, force):
    """
    Klasyfikuje stronę.

    :param url: adres strony
    :param filename: plik z wpisami treningowymi
    :param force: wymusza ponowne nauczenie klasyfikatora
    :returns: przewidziana kategoria
    """
    print "getting"
    cl = get_classifier(filename=filename, force=force)
    print "get cl"
    result = cl.classify(url)
    return result


def update_website(url, category):
    """
    Funkcja służąca do douczania klasyfikatora.

    :param url: adres strony
    :param category: poprawna kategoria
    :returns: Komunikat o powodzeniu
    """
    cl = get_classifier()
    entry = [{'category': category, 'url': url}]
    cl.train(entry)
    save_classifier(cl)
    return "Updated"


def get_classifier(filename="websites.txt", partition=1, force=False):
    """
    Zwraca wytrenowany klasyfikator, trenowany na nowo lub odczytany z pliku.

    :param filename: ścieżka do pliku z wpisami uczącymi
    :param partition: float, część wpisów jaka ma znaleźć się w zbiorze treningowym
    :param force: wymusza ponowne uczenie
    :returns: klasyfikator
    """
    if not force:
        try:
            return load_classifier(filename, partition)
        except:
            pass
    print "training"
    cl = train_classifier(filename, partition)
    save_classifier(cl, filename, partition)
    return cl


def get_train_eval_sets(filename, partition):
    """
    Odczytuje wpisy i rozdziela zbiór wpisów na zbiór treningowy i testujący.

    :param filename: ścieżka do pliku
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :returns: zbiór trenignowy, zbiór testujący
    """
    entries = datasource.get_raw_entries(filename)
    train_set, eval_set = classifier.get_train_eval_sets(entries, partition)
    return train_set, eval_set


def train_classifier(filename, partition):
    """
    Zwraca wytrenowany klasyfikator na odpowiedniej części pełnego zbioru.

    :param filename: ścieżka do pliku
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :returns: wytrenowany klasyfikator
    """
    train_set, eval_set = get_train_eval_sets(filename, partition)
    cl = classifier.get_trained_classifier(train_set)
    return cl


def save_classifier(cl, filename="websites.txt", partition=1):
    """
    Serializuje i zapisuje klasyfikator do pliku.

    :param cl: klasyfikator
    :param filename: ścieżka do pliku z wpisami
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    """
    picklename = get_classifier_picklename(filename, partition)
    with open(picklename, "w+b") as f:
        pickle.dump(cl, f, pickle.HIGHEST_PROTOCOL)


def load_classifier(filename, partition):
    """
    Ładuje klasyfkator z pliku.

    :param filename: ścieżka do pliku z wpisami
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :return klasyfkator
    """
    picklename = get_classifier_picklename(filename, partition)
    with open(picklename, 'rb') as f:
        cl = pickle.load(f)
        return cl


def get_classifier_picklename(filename, partition):
    """
    Zwraca nazwę pliku odpowiedniego klasyfikatora.

    :param filename: ścieżka do pliku z wpisami
    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :returns: nazwa pliku
    """
    return "cl_{}_{}_.pickle".format(filename, partition)


def get_accuracy(partition, filename="websites.txt"):
    """
    Zwraca stosunek poprawnie przewidzianych wpisów do pełnej ich liczby.

    :param partition: float, część jaka ma znaleźć się w zbiorze treningowym
    :param filename: ścieżka do pliku z wpisami
    :returns: poprawnie przewidziane/pełna liczba
    """
    train, eval = get_train_eval_sets(filename, partition)
    cl = classifier.get_trained_classifier(train)
    return cl.accuracy(eval)


def get_cross_val(folds, filename="websites.txt"):
    """
    Wykonuje walidację krzyżową z odpowiednią liczbą podzbiorów.

    :param folds: liczba podzbiorów na które zostanie podzielony zbiór wpisów
    :param filename: ścieżka do pliku z wpisamis
    :returns: wynik walidacji krzyżowej
    """
    entries = datasource.get_raw_entries(filename)
    # random.seed(123)
    random.shuffle(entries)
    clf = classifier.get_classifier()
    return clf.xval(entries, folds)


if __name__ == '__main__':
    print classify_website("tvn24.pl", "websites.txt", False)
