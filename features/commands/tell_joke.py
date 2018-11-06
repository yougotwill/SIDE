import sublime
import sublime_plugin

from urllib.request import Request, urlopen

class SideTellJoke(sublime_plugin.TextCommand):
    def run(self, edit):
        req = Request("https://geek-jokes.sameerkumar.website/api", headers={'User-Agent': 'Mozilla/5.0'})
        contents = urlopen(req).read().decode('utf-8')
        self.view.show_popup(contents, max_width=500)
