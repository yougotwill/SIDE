import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import definition, get_word, open_view, chose_one_location_from_many, find_symbols, get_region_between_symbols, filter_regions_by_scope_name, filter_regions_by_region


class SideDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        """ index - if specified goto that index location. """
        window = sublime.active_window()
        point = self.view.sel()[0].begin()
        word = get_word(self.view, point)
        locations = definition(word, self.view)

        if len(locations) == 0:
            symbols = find_symbols(self.view)            
            word_regions = self.view.find_all(r"\b{}\b".format(word))

            between_symbols_region = get_region_between_symbols(point, symbols, self.view)
            words_between_regions = filter_regions_by_region(word_regions, between_symbols_region)
            scope_name = self.view.scope_name(point)
            words_between_regions = filter_regions_by_scope_name(words_between_regions, scope_name, self.view)  

            # make sure that there is at least one item in list
            if len(words_between_regions) < 1:
                return 

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