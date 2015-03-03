# coding=utf-8
import csv
import os.path
import urlparse

from selenium.common.exceptions import TimeoutException
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver


def fetch_website(url):
    """
    Pobiera stronę internetową. Próbuje wykonać JS, jeśli trwa to zbyt długo pobiera html.
    
    :param url: adres strony
    :returns: html
    """
    print "Fetching", url
    full_url = get_full_url(url)
    try:
        response = fetch_website_js(full_url)
    except TimeoutException:
        print "JS Timeout, fetching HTML"
        response = fetch_website_html(full_url)
    return response.encode('utf-8')


def get_full_url(url):
    """
    Zwraca pełny adres strony internetowej.

    :param url: adres strony
    :returns: pełny adres strony
    """
    http = "http"
    www = "www."
    if url.startswith(http):
        full_url = url
    elif url.startswith(www):
        full_url = "http://" + url
    else:
        full_url = "http://www." + url
    return full_url


def fetch_website_js(url):
    """
    Pobiera stronę za pomocą przeglądarki pozbawionej interfejsu graficznego i wykonuje javascript.

    :param url: adres strony
    :returns: html
    """
    timeout = 20
    browser = get_browser()
    browser.set_page_load_timeout(timeout)
    browser.get(url)
    response = browser.execute_script("return document.documentElement.innerHTML;")
    browser.quit()
    return response


def fetch_website_html(url):
    """
    Pobiera html strony nie wykonując javascriptu.

    :param url: adres strony
    :returns: html
    """
    user_agent_setting = {'User-Agent':
                              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"}
    r = requests.get(url, headers=user_agent_setting)
    if r.status_code == 200:
        return r.text


def get_browser():
    """
    Zwraca obiekt przeglądarki pozbawionej interfejsu graficznego z odpowiednimi ustawieniami.

    :returns: PhantomJS WebDriver
    """
    user_agent = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"""

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent

    driver = webdriver.PhantomJS("node_modules/phantomjs/lib/phantom/bin/phantomjs", desired_capabilities=dcap)
    return driver


def save_website(url, text):
    """
    Zapisuje kod strony na dysku.

    :param url: adres strony
    :param text: kod strony
    """
    path = get_path(url)
    if text:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w+') as f:
            f.write(text)


def pull_websites(websites, force=False):
    """
    Pobiera strony internetowe.

    :param websites: zbiór stron do pobrania
    :param force: określa czy wymuszać pobieranie na nowo zamiast odczytywania z dysku
    """
    urls = []
    for site in websites:
        urls.append(site['url'])

    for url in urls:
        print "Getting:", url
        get_website(url, force)


def pull_website(url):
    """
    Pobiera stronę internetową i ją zapisuje na dysku.

    :param url: adres strony
    :returns: kod strony
    """
    text = ""
    try:
        text = fetch_website(url)
        save_website(url, text)
    except Exception as e:
        print "An error occured: ", e
    return text


def read_entries(filename):
    """
    Odczytuje wpisy z pliku csv.

    :param filename: ścieżka do pliku
    :returns: wpisy
    """
    entries = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        for row in reader:
            entries.append(row)
    return entries


def get_path(url):
    """
    Zwrraca ścieżkę do pliku z zapisaną stroną internetową.

    :param url: adres strony
    :returns: ścieżka
    """
    directory = "websites/"
    ext = ""
    if not (url.endswith("html") or url.endswith("htm")):
        ext = ".html"
    return directory + escape_filename(url) + ext


def escape_filename(url):
    """
    Zamienia znaki w adresie aby uzyskać poprawną nazwę pliku.

    :param url: adres strony
    :returns: nazwa pliku
    """
    result = urlparse.urlparse(url)
    no_http = "".join(result[1:])
    escaped = no_http.replace("/", "_")
    return escaped


def get_website(url, force=False):
    """
    Zwraca stronę internetową.

    :param url: adres strony
    :param force: określa czy wymuszać pobieranie na nowo zamiast odczytywania z dysku
    :returns: html
    """
    if not force:
        path = get_path(url)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
    text = pull_website(url)
    return text


def get_raw_entries(filename="websites.txt"):
    """
    Zwraca wpisy z pliku.

    :param filename: ścieżka do pliku
    :returns: lista słowników zawierających url i kategorię
    """
    entries = read_entries(filename)
    return entries


if __name__ == '__main__':
    entries = read_entries("websites.txt")
    pull_websites(entries, force=False)
    # print escape_filename("http://www.forum.muratordom.pl/showthread.php?74534-Pogadajmy-o-pierdo%C5%82ach")
