import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import find_symbols


class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        point = locations[0]

        # dont commplete in strings
        is_in_string = self.view.match_selector(point, 'string.quoted')
        if is_in_string:
            return None        

        window = sublime.active_window()
        views = window.views()
        
        symbols = find_symbols(self.view, views)
        completions = []
        # easy way to filter out hash completions
        unique_symbols = []
        for symbol_location in symbols:
            _file_name, base_file_name, _region, symbol, symbol_type = symbol_location
            completion_item = ["{}\t{}{}".format(symbol, base_file_name, symbol_type), "{}".format(symbol)]
            if symbol not in unique_symbols:
                unique_symbols.append(symbol)
            if completion_item not in completions:
                completions.append(completion_item)

        for view in views:
            hash_completions = view.extract_completions(prefix)
            for completion in hash_completions:
                if completion in unique_symbols:
                    continue
                completion_item = ["{}\t{}".format(completion, '[#]'), "{}".format(completion)]
                completions.append(completion_item)

        return (completions, sublime.INHIBIT_WORD_COMPLETIONS)
