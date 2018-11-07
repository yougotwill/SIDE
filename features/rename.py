import sublime
import sublime_plugin

from functools import reduce
from SIDE.features.lib.helpers import get_word, find_symbols


class SideRename(sublime_plugin.TextCommand):
    def run(self, edit, find_all=True):
        symbols = find_symbols(self.view)
        # type List[reigion]
        regions = list(map(lambda l: l[2], symbols))

        point = self.view.sel()[0].begin()

        between_symbols = None  # Region
        # check to see if the point is between two symbols
        for index, region in enumerate(regions):          
            if index == len(regions) - 1:
                a = region.begin()
                b = self.view.size()
                reg = sublime.Region(a, b)
                if reg.contains(point):
                    between_symbols = reg
            else:
                a = region.begin()
                nexe_region = regions[index+1]
                b = nexe_region.begin()
                reg = sublime.Region(a, b)
                if reg.contains(point):
                    between_symbols = reg
        
        word = get_word(self.view)
        word_regions = self.view.find_all(r"\b{}\b".format(word))
        between_regions = []
        if between_symbols is not None:
            for region in word_regions:
                if between_symbols.contains(region):
                    between_regions.append(region)

        # useful for debuging
        # # if between_symbols is not None:
        #     self.view.add_regions('function', [between_symbols], 'comment', flags=sublime.DRAW_OUTLINED)
        # self.view.add_regions('word', between_regions, 'stirng', flags=sublime.DRAW_OUTLINED)        

        sel = self.view.sel()
        sel.clear()
        if len(between_regions) > 0 and not find_all:
            # select all word occurances beetween two symbols
            sel.add_all(between_regions)
        else:
            # select all word occurances in the file
            sel.add_all(word_regions)

       