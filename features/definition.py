import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import defintion, get_word, history, open_view, chose_one_location_from_many


class SideJumpBack(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        id = window.id()
        bookmarks = history.get(id, [])
        
        if len(bookmarks) > 0:
            bookmark = bookmarks.pop()
            file_path, row_col = bookmark 
            row, col = row_col
            window.open_file("{}:{}:{}".format(file_path, row, col), sublime.ENCODED_POSITION)
        else:
            self.view.run_command('jump_back')


class SideDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        word = get_word(self.view)
        locations = defintion(word, self.view)

        if len(locations) == 0:
            return

        if len(locations) == 1:
            open_view(locations[0], self.view)
            return
        
        if len(locations) > 1:
            chose_one_location_from_many(locations, self.view)