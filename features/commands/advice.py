import sublime_plugin
import threading
import json

from urllib.request import Request, urlopen
from html import escape


def send_request(view):
    req = Request("https://api.adviceslip.com/advice", headers={'User-Agent': 'Mozilla/5.0'})
    try:
        json_data = json.loads(urlopen(req).read().decode('utf-8'))
        contents = json_data['slip']['advice']
    except:
        contents = 'What Dana once said... Zivot je kratak, pojedi batak 😎'
    contents = contents.replace('&quot;', '\'')
    view.show_popup("<p style='padding: 20px 10px 20px 10px'>{}</p>".format(escape(contents, False)), max_width=500)   


class SideAdvice(sublime_plugin.TextCommand):
    def run(self, edit):
        t = threading.Thread(target=send_request, args=(self.view,))
        t.start()
        