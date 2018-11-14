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
        for symbol_location in symbols:
            _file_name, base_file_name, _region, symbol, symbol_type = symbol_location
            completion_item = ["{}\t{}{}".format(symbol, base_file_name, symbol_type), "{}".format(symbol)]
            completions.append(completion_item)

        for view in views:
            hash_completions = view.extract_completions(prefix)
            for completion in hash_completions:
                completion_item = ["{}\t{}".format(completion, '[#]'), "{}".format(completion)]
                if completion_item in completions:
                    continue
                completions.append(completion_item)

        return completions
