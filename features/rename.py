import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word, find_symbols, scroll_to_not_visible_region, get_region_between_symbols, is_function, filter_regions_by_scope_name, filter_regions_by_region


class SideRename(sublime_plugin.TextCommand):
    def run(self, edit, find_all=True):
        symbols = find_symbols(self.view)

        point = self.view.sel()[0].begin()
        word = get_word(self.view, point)
        word_regions = self.view.find_all(r"\b{}\b".format(word))

        between_symbols_region = get_region_between_symbols(point, symbols, self.view)
        words_between_regions = filter_regions_by_region(word_regions, between_symbols_region)
        scope_name = self.view.scope_name(point)
        words_between_regions = filter_regions_by_scope_name(words_between_regions, scope_name, self.view)        

        # useful for debuging
        # # if between_symbols_region is not None:
        #     self.view.add_regions('function', [between_symbols_region], 'comment', flags=sublime.DRAW_OUTLINED)
        # self.view.add_regions('word', words_between_regions, 'stirng', flags=sublime.DRAW_OUTLINED)        

        sel = self.view.sel()
        if len(words_between_regions) > 0 and not find_all:
            # select all word occurances beetween two symbols
            sel.clear()
            sel.add_all(words_between_regions)
            scroll_to_not_visible_region(words_between_regions, self.view)
        elif len(word_regions) > 0:
            # select all word occurances in the file
            sel.clear()
            sel.add_all(word_regions)
            scroll_to_not_visible_region(word_regions, self.view)

       