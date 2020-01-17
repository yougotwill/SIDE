import sublime_plugin
import threading

from urllib.request import Request, urlopen
from html import escape


def send_request(view):
    req = Request("https://geek-jokes.sameerkumar.website/api", headers={'User-Agent': 'Mozilla/5.0'})
    try:
        contents = urlopen(req).read().decode('utf-8')
    except:
        contents = 'Without the Internet, my humor is gone :('
    contents = contents.replace('&quot;', '\'')
    view.show_popup("<p style=\"padding: 20px 10px 30px 10px; position: static\">{}</p>".format(escape(contents, False)), max_width=500)


class SideTellJoke(sublime_plugin.TextCommand):
    def run(self, edit):
        t = threading.Thread(target=send_request, args=(self.view,))
        t.start()
        
        
