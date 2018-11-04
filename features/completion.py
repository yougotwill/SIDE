import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import find_symbols


class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        point = locations[0]
        is_irrelevant = self.view.match_selector(point, 'string.quoted')
        if is_irrelevant:
            return None
        
        window = sublime.active_window()
        views = window.views()
        
        symbols = find_symbols(self.view, views)
        completions = []
        for symbol_location in symbols:
            file_name, base_file_name, region, symbol, symbol_type = symbol_location
            completion_item = ["{}\t{}{}".format(symbol, base_file_name, symbol_type), "{}($1)$0".format(symbol)]
            completions.append(completion_item)

        return (completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS)

