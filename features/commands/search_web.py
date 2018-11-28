import os
import sublime
import sublime_plugin
import webbrowser as wb


class SideSearchWeb(sublime_plugin.TextCommand):
    def run(self, edit): 
        # grab the words in region
        region = self.view.sel()[0]
        word = self.view.substr(region).strip()

        # if no region, grab the word under cursor
        if len(word) == 0:
            word = self.view.substr(self.view.word(region.begin())).strip()

        filename, file_extension = os.path.splitext(self.view.file_name())
        
        search_term = "https://www.google.com/search?q={} {}".format(file_extension.strip('.'), word)
        wb.open_new_tab(search_term)