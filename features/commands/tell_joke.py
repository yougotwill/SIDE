import sublime
import sublime_plugin

from urllib.request import Request, urlopen
from html import escape

class SideTellJoke(sublime_plugin.TextCommand):
    def run(self, edit):
        req = Request("https://geek-jokes.sameerkumar.website/api", headers={'User-Agent': 'Mozilla/5.0'})
        contents = urlopen(req).read().decode('utf-8')
        contents = contents.replace('&quot;', '\'')
        self.view.show_popup(escape(contents, False), max_width=500)