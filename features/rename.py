import sublime
import sublime_plugin

from functools import reduce
from SIDE.features.lib.helpers import get_word, find_symbols


class SideRename(sublime_plugin.TextCommand):
    def run(self, edit):
        point = self.view.sel()[0].begin()
        symbols = find_symbols(self.view) 
        # type [(region, symbol_type)]
        symbols = list(map(lambda l: (l[2], l[4]),symbols))

        print('sym', symbols)
        word = get_word(self.view)

        rename_regions = []
        for index, symbol in enumerate(symbols):
            region, symbol_type = symbol
          
            if index == len(symbols) - 1:
                a = region.begin()
                b = self.view.size()
                reg = sublime.Region(a, b)
                if reg.contains(point):
                    rename_regions.append(reg)
            else:
                a = region.begin()
                nexe_region, next_symbol_type = symbols[index+1]
                b = nexe_region.begin()
                reg = sublime.Region(a, b)
                if reg.contains(point):
                    rename_regions.append(reg)

        # useful for debuging
        # self.view.add_regions('function', rename_regions, 'comment', flags=sublime.DRAW_OUTLINED)
        
        word_regions = self.view.find_all(r"\b{}\b".format(word))
        final = []
        if len(rename_regions) > 0:
            for r in word_regions:
                if rename_regions[0].contains(r):
                    final.append(r)
        # useful for debuging
        # self.view.add_regions('word', final, 'stirng', flags=sublime.DRAW_OUTLINED)        

        if len(final) > 0:
            print('here')
            sel = self.view.sel()
            sel.clear()
        
            sel.add_all(final)
        else:
            print('or here')
            window = sublime.active_window()

            window.run_command('find_all_under')

       