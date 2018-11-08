import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import definition, get_word, history, open_view, chose_one_location_from_many, find_symbols, get_region_between_symbols, filter_region_between_regions


class SideJumpBack(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        id = window.id()
        bookmarks = history.get(id, [])

        if len(bookmarks) > 0:
            bookmark = bookmarks.pop()
            file_path, row_col = bookmark 
            row, col = row_col
            v = window.find_open_file(file_path)
            if v is not None:
                window.focus_view(v)
                point = v.text_point(row, col)
                sel = v.sel()
                sel.clear()
                sel.add(point)
                v.show_at_center(point)
            else:
                window.open_file("{}:{}:{}".format(file_path, row + 1, col + 1), sublime.ENCODED_POSITION)
        else:
            self.view.run_command('jump_back')


class SideDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        point = self.view.sel()[0].begin()
        word = get_word(self.view, point)
        locations = definition(word, self.view)

        if len(locations) == 0:
            symbols = find_symbols(self.view)            
            word_regions = self.view.find_all(r"\b{}\b".format(word))

            between_symbols_region = get_region_between_symbols(point, symbols, self.view)
            words_between_regions = filter_region_between_regions(between_symbols_region, word_regions)

            definition_point = words_between_regions[0].begin()
            file_name = self.view.file_name()
            row, col = self.view.rowcol(definition_point)
            row += 1
            col += 1
            location = (file_name, None, (row, col))
            open_view(location, self.view)
            return

        if len(locations) == 1:
            open_view(locations[0], self.view)
            return
        
        if len(locations) > 1:
            chose_one_location_from_many(locations, self.view)