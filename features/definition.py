import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import defintion, get_word, history, open_view


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
            quick_panel = {
                'labels': [],
                'on_select': []
            }

            for location in locations:
                file_path, relative_file_path, row_col = location
                row, col = row_col
                quick_panel['labels'].append("{}:{}:{}".format(relative_file_path, row, col))
                quick_panel['on_select'].append(location)
            
            def _on_done(index):
                if index == -1:
                    window.focus_view(self.view)
                    return 
                location =  quick_panel['on_select'][index]
                open_view(location, self.view)

            def _on_change(index):                    
                location = quick_panel['on_select'][index]
                open_view(location, self.view, sublime.ENCODED_POSITION | sublime.TRANSIENT)

            window.show_quick_panel(
                quick_panel['labels'],
                _on_done,
                on_highlight=_on_change
            )