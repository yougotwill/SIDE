import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import defintion, get_word


history = []


class SideJumpBack(sublime_plugin.TextCommand):
    def run(self, edit):
        if len(history) > 0:
            bookmark = history.pop()
            file_path, row_col = bookmark 
            row, col = row_col
            window = sublime.active_window()
            window.open_file("{}:{}:{}".format(file_path, row, col), sublime.ENCODED_POSITION)
        else:
            self.view.run_command('jump_back')


class SideDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        word = get_word(self.view)
        locations = defintion(word, self.view)

        if len(locations) == 0:
            window.run_command("goto_definition")
            return

        if len(locations) == 1:
            old_cursor_pos = self.view.sel()[0].begin()
            old_row, old_col = self.view.rowcol(old_cursor_pos)
            # normalize row and column
            old_row += 1
            old_col += 1
            bookmark = (self.view.file_name(), (old_row, old_col))

            file_path, _rel_file_path, row_col = locations[0]
            new_row, new_col = row_col
            
            # save bookmark 
            if old_row != new_row:
                history.append(bookmark)
            # open location
            window.open_file("{}:{}:{}".format(file_path, new_row, new_col), sublime.ENCODED_POSITION)
        
        if len(locations) > 1:
            quick_panel = {
                'labels': [],
                'on_select': []
            }

            for location in locations:
                file_path, relative_file_path, row_col = location
                row, col = row_col
                quick_panel['labels'].append("{}:{}:{}".format(relative_file_path, row, col))
                quick_panel['on_select'].append("{}:{}:{}".format(file_path, row, col))
            
            def _on_done(index):
                if index == -1:
                    window.focus_view(self.view)
                    return 
                file_path_row_col =  quick_panel['on_select'][index]
                window.open_file("{}".format(file_path_row_col), sublime.ENCODED_POSITION)

            def _on_change(index):                    
                file_path_row_col = quick_panel['on_select'][index]
                preview_view = window.open_file("{}".format(file_path_row_col), 
                                                sublime.ENCODED_POSITION | sublime.TRANSIENT)

            window.show_quick_panel(
                quick_panel['labels'],
                _on_done,
                on_highlight=_on_change
            )