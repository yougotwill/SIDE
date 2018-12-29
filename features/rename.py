import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word, find_symbols, scroll_to_not_visible_region, get_region_between_symbols, is_function, filter_regions_by_scope_name, filter_regions_by_region, get_word_regions


class SideRename(sublime_plugin.TextCommand):
    def run(self, edit, find_all=True):

        word_regions ,words_between_regions = get_word_regions(self.view)        

        sel = self.view.sel()
        if len(words_between_regions) > 0 and not find_all:
            # select all word occurrences between two symbols
            sel.clear()
            sel.add_all(words_between_regions)
            scroll_to_not_visible_region(words_between_regions, self.view)
        elif len(word_regions) > 0:
            # select all word occurrences in the file
            sel.clear()
            sel.add_all(word_regions)
            scroll_to_not_visible_region(word_regions, self.view)

       