#!/usr/bin/env python
# coding=utf-8
import urllib
import web
import json
import main

urls = (
    '/classify/(.*)', 'classify',
    '/classify', 'classify'
)

app = web.application(urls, globals())


class classify:

    def GET(self, url):
        """
        Zwraca odpowiedź na żądanie GET.

        :param url: adres storny
        :returns: json z odpowiedzią
        """
        url = urllib.unquote(url)
        resp = main.classify_website(url, "websites.txt", False)
        return json.dumps(resp)

    def POST(self):
        """
        Zwraca odpowiedź na żądanie POST.

        :returns: json z odpowiedzią
        """
        data = web.data()
        d = json.loads(data)
        url = d["url"]
        cat = d["category"]
        resp = main.update_website(url, cat)
        return resp

if __name__ == "__main__":
    app.run()
