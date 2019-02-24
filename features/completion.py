import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import find_symbols
from SIDE.features.indexer import panel_state


class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        global panel_state
        point = locations[0] 

        views = self.sort_views_by_relevance()
        
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
                # filter out unique symols or words in comment like "don't"  
                if completion in unique_symbols or "'" in completion or '.' in completion:
                    continue
                unique_symbols.append(completion)
                completion_item = ["{}\t{}".format(completion, '[#]'), "{}".format(completion)]
                completions.append(completion_item)

        return (completions, sublime.INHIBIT_WORD_COMPLETIONS)

    def sort_views_by_relevance(self):
        """ Get a list of sorted views. This ensures we get the most relevant suggestions. """
        window = sublime.active_window()

        # add the current view is the most relevant
        views = [self.view]
        try:
            # the second most relevant suggestions are from the indexed panels
            for panel_name in panel_state:
                panel = window.find_output_panel(panel_name)
                panel.file_name = lambda v=panel_name: v 
                views.append(panel)
        except Exception as e:
            print('No panel', e)

        # the last but not least are the open views
        for view in window.views():
            if view is not self.view:
                views.append(view)

        return views

    def on_modified_async(self): 
        if self.view.is_auto_complete_visible():
            word = self.view.substr(self.view.word(self.view.sel()[0].begin()))
            if len(word) == 1:
                self.view.run_command('hide_auto_complete')
                self.view.run_command("auto_complete", {
                    'disable_auto_insert': True,
                    # 'next_completion_if_showing': False
                })