import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word, find_symbols, scroll_to_not_visible_region, get_region_between_symbols, is_function, filter_regions_by_scope_name, filter_regions_by_region

def get_word_regions(view):
    ''' Returns a tuple containing two lists 
        first list contain regions of all word occurrences in the view
        second list contain regions of word occurrences between two closes symbols. 
        Used for renaming and highlighting. '''
    symbols = find_symbols(view)

    point = view.sel()[0].begin()
    word = get_word(view, point)
    word_regions = view.find_all(r"\b{}\b".format(word))

    between_symbols_region = get_region_between_symbols(point, symbols, view)
    words_between_regions = filter_regions_by_region(word_regions, between_symbols_region)
    scope_name = view.scope_name(point)
    words_between_regions = filter_regions_by_scope_name(words_between_regions, scope_name, view) 

    # useful for debugging
    # if between_symbols_region is not None:
    #     view.add_regions('function', [between_symbols_region], 'comment', flags=sublime.DRAW_OUTLINED)
    # view.add_regions('word', words_between_regions, 'string', flags=sublime.DRAW_OUTLINED)        

    return (word_regions, words_between_regions)


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

       