import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import defintion, get_word


history = []


class SideJumpBack(sublime_plugin.TextCommand):
    def run(self, edit):
        if len(history):
            bookmark = history.pop()
            file_path, row_col = bookmark 
            row, col = row_col
            window = sublime.active_window()
            window.open_file("{}:{}:{}".format(file_path, row+1, col+1), sublime.ENCODED_POSITION)
        else:
            self.view.run_command('jump_back')


class SideDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        cursor_pos = self.view.sel()[0].begin()
        word = get_word(self.view)

        locations = defintion(word, self.view)

        if len(locations) == 0:
            window.run_command("goto_definition")
            return

        if len(locations) == 1:
            window = sublime.active_window()
            location = locations[0]
            file_path, relative_file_path, row_col = location
            row, col = row_col
            bookmark = (self.view.file_name(), self.view.rowcol(cursor_pos))
           
            history.append(bookmark)
            window.open_file("{}:{}:{}".format(file_path, row, col), sublime.ENCODED_POSITION)
        
        if len(locations) > 1:
            definitions = []
            full_path_definitions = []
            for location in locations:
                file_path, relative_file_path, row_col = location
                row, col = row_col
                definitions.append("{}:{}:{}".format(relative_file_path, row, col))
                full_path_definitions.append("{}:{}:{}".format(file_path, row, col))

            
            preview_view = None
            def _on_done(index):
                if index == -1:
                    window.focus_view(self.view)
                    return 
                file_path =  full_path_definitions[index]
                window.open_file("{}".format(file_path), sublime.ENCODED_POSITION)

            def _on_change(index):                    
                file_path =  full_path_definitions[index]
                preview_view = window.open_file("{}".format(file_path), sublime.ENCODED_POSITION | sublime.TRANSIENT)

            window.show_quick_panel(
                definitions,
                _on_done,
                on_highlight=_on_change
            )