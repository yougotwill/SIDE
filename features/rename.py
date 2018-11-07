import sublime
import sublime_plugin

from functools import reduce
from SIDE.features.lib.helpers import get_word, find_symbols, scroll_to_not_visible_region, point_beetween_regions




class SideRename(sublime_plugin.TextCommand):
    def run(self, edit, find_all=True):
        symbols = find_symbols(self.view)
        # type List[reigion]
        regions = list(map(lambda l: l[2], symbols))
        point = self.view.sel()[0].begin()

        between_symbols_region = point_beetween_regions(point, regions, self.view) 
        
        word = get_word(self.view)
        word_regions = self.view.find_all(r"\b{}\b".format(word))

        word_between_regions = []
        if between_symbols_region is not None:
            for region in word_regions:
                if between_symbols_region.contains(region):
                    word_between_regions.append(region)

        # useful for debuging
        # # if between_symbols_region is not None:
        #     self.view.add_regions('function', [between_symbols_region], 'comment', flags=sublime.DRAW_OUTLINED)
        # self.view.add_regions('word', word_between_regions, 'stirng', flags=sublime.DRAW_OUTLINED)        

        sel = self.view.sel()
        sel.clear()
        if len(word_between_regions) > 0 and not find_all:
            # select all word occurances beetween two symbols
            sel.add_all(word_between_regions)
            scroll_to_not_visible_region(word_between_regions, self.view)
        else:
            # select all word occurances in the file
            sel.add_all(word_regions)
            scroll_to_not_visible_region(word_regions, self.view)

       