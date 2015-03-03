# coding=utf-8
import nltk
from bs4 import BeautifulSoup
import re

import pl_stemmer
import datasource


def get_text_from_html(html):
    """
    Zwraca tekst strony po sanityzacji.
    
    :param html: kod strony
    :returns: tekst
    """
    text = get_raw_text_from_html(html)
    text = sanitize_text(text)
    return text


def get_raw_text_from_html(html):
    """
    Wyciąga surowy tekst z html.
    
    :param html: kod strony
    :returns: tekst
    """
    bs = BeautifulSoup(unicode(html, 'utf-8'))
    # kill all script and style elements
    for script in bs(["script", "style"]):
        script.extract()  # rip it out

    text = bs.get_text()
    bs = BeautifulSoup(text)
    text = bs.get_text()
    return text


def sanitize_text(raw_text):
    """
    Dokonuje podstawowej sanityzacji tekstu.
    
    :param raw_text: tekst przed obróbką
    :returns: tekst po sanityzacji
    """
    lines = (line.strip() for line in raw_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    text = "".join(break_on_upper(text))
    return text


def space_before_upper(char, char_before):
    """
    Wstawia spację przed dużą literą, rozdzielając w ten sposób słowa, chyba że poprzedni znak to też duża litera.

    :param char: znak
    :param char_before: poprzedni znak
    :returns: spacja + znak lub znak
    """
    if char.isupper() and not (char_before.isupper() or char_before.isspace() or char_before == '"' or char_before == "'"):
        return " " + char
    else:
        return char


def char_before(text, i):
    """
    Zwraca poprzedni znak względem indeksu.

    :param text: tekst
    :param i: indeks
    :returns: poprzedni znak lub pusty string
    """
    if i != 0:
        return text[i - 1]
    else:
        return ""


def break_on_upper(text):
    """
    Wstawia spacje przed dużymi literami.

    :param text: tekst
    :returns: poprawiony tekst
    """
    return [space_before_upper(c, char_before(text, i)) for i, c in enumerate(text)]


def stem_word(word):
    """
    Dokonuje stemmingu słowa z języka polskiego.

    :param word: słowo
    :returns: stem słowa
    """
    word = pl_stemmer.remove_adjective_ends(word)
    word = pl_stemmer.remove_adverbs_ends(word)
    word = pl_stemmer.remove_diminutive(word)
    word = pl_stemmer.remove_general_ends(word)
    word = pl_stemmer.remove_nouns(word)
    word = pl_stemmer.remove_plural_forms(word)
    word = pl_stemmer.remove_verbs_ends(word)
    return word


def stem(wordlist):
    """
    Dokonuje stemmingu listy słów z języka polskiego.

    :param wordlist: lista słów
    :returns: lista stemów
    """
    return [stem_word(word) for word in wordlist]


stopwords = {unicode(line.strip(), 'utf-8') for line in open('polish-stopwords.txt')}
def get_stopwords():
    """
    Zwraca listę często występujących słów w języku polskim.

    :returns: lista słów
    """
    return stopwords


def tokenize(text):
    """
    Dzieli tekst na tokeny - pojedyncze slowa.

    :param text: tekst
    :returns: lista tokenow
    """
    # De facto działanie jak poniżej:
    tokens = nltk.word_tokenize(text)

    # tokenizer = nltk.data.load('nltk:tokenizers/punkt/polish.pickle')
    # sentences = tokenizer.tokenize(text)
    # tokens = []
    # for sentence in sentences:
    # tokens.extend(TreebankWordTokenizer().tokenize(sentence))
    return tokens


def filter_short(token):
    """
    Funkcja służąca do wycina krótkich słów i znaków o długości mniejszej niż 2.

    :param token: token
    :returns: True jeśli dłuższe niż 1, False w.p.p.
    """
    if len(token) > 1:
        return True
    else:
        return False


def filter_nonalnum(token):
    """
    Wycina znaki niealfanumeryczne ze słów.

    :param token: token
    :returns: token pozbawiony znaków niealfanumerycznych
    """
    return "".join([c for c in token if c.isalnum()])


def get_filtered_text(url):
    """
    Zwraca tekst strony po sanityzacji i filtracji.

    :param url: adres strony
    :returns: tekst strony po filtracji
    """
    text = get_nonfiltered_text(url)
    filtered = filter_text(text)
    return " ".join(filtered)


def get_nonfiltered_text(url):
    """
    Zwraca tekst po sanityzacji, ale bez filtracji.

    :param url: adres strony
    :returns: tekst strony po sanityzacji
    """
    html = datasource.get_website(url)
    text = get_text_from_html(html)
    return text


def filter_text(text, stemming=True):
    """
    Filtruje tekst - tokenizuje, wycina powszechne słowa, filtruje krótkie i opcjonalnie stemuje.

    :param text: tekst
    :param stemming: flaga czy stemować
    :returns: przefiltrowane tokeny
    """
    stopwords = get_stopwords()

    tokens = tokenize(text)
    tokens = [filter_nonalnum(t).lower() for t in tokens]
    if stemming:
        tokens = stem(tokens)
    tokens = [word for word in tokens if word not in stopwords]
    tokens = filter(filter_short, tokens)
    return tokens


def get_link_text_length(html):
    """
    Zwraca długość tekstu w linkach i całego tekstu.

    :param html: kod html strony
    :returns: długość tekstu w linkach, długość całego tekstu
    """
    bs = BeautifulSoup(unicode(html, 'utf-8'))

    links = bs.find_all('a')
    link_text = []
    for l in links:
        l_text = l.get_text()
        if l_text:
            link_text.append("".join([c for c in l_text if c.isalnum()]))
    link_text_length = get_list_elements_len(link_text)

    full_text = get_raw_text_from_html(html)

    full_text_length = len("".join([c for c in full_text if c.isalnum()]))
    return float(link_text_length), float(full_text_length)


def get_menu_features_text(html):
    """
    Zwraca tekst złożony ze słów występujących w menu strony.

    :param html: html strony
    :returns: tekst złożony ze słów występujących w menu strony
    """
    soup = BeautifulSoup(unicode(html, 'utf-8'))
    menus = soup.find_all(attrs={'class': re.compile('[Mm]enu')})
    navs = soup.find_all(attrs={'class': re.compile('[Nn]av')})
    menuid = soup.find_all(attrs={'id': re.compile('[Mm]enu')})
    navsid = soup.find_all(attrs={'id': re.compile('[Nn]av')})
    menus.extend(navs)
    menus.extend(menuid)
    menus.extend(navsid)
    elements = []
    for d in menus:
        t = d.get_text()
        s = BeautifulSoup(t)
        elements.extend(filter_text(sanitize_text(s.get_text())))
    return " ".join(elements)


def get_list_elements_len(l):
    """
    Zwraca sumaryczną długość elementów listy.

    :param l: lista elementów
    :returns: sumaryczna długość
    """
    s = 0
    for e in l:
        s += len(e)
    return s


if __name__ == '__main__':
    print get_link_text_length(datasource.get_website("onet.pl"))