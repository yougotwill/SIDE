import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import find_symbols, find_references, debug
from SIDE.features.indexer import panel_state

class SideCompletion(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        super().__init__(view)
        self.last_symbols_len = -1
        self.items = []

    def on_query_completions(self, prefix, locations):
        completions = sublime.CompletionList()

        views = self.sort_views_by_relevance()
        symbols = find_symbols(self.view, views)

        # some simple caching strategy
        if len(symbols) == self.last_symbols_len:
            completions.set_completions(self.items)
            return completions

        self.last_symbols_len = len(symbols)
        self.items = []

        # easy way to filter out hash completions
        unique_symbols = []
        for symbol_location in symbols:
            _file_name, base_file_name, _region, symbol, symbol_type = symbol_location
            completion_item = sublime.CompletionItem(
                symbol,
                annotation=base_file_name,
                completion=symbol,
                kind=(sublime.KIND_ID_AMBIGUOUS, symbol_type, '')
            )
            if symbol not in unique_symbols:
                unique_symbols.append(symbol)
                self.items.append(completion_item)

        references = find_references(self.view, views)
        for symbol_location in references:
            _file_name, base_file_name, _region, symbol, symbol_type = symbol_location

            completion_item = sublime.CompletionItem(
                symbol,
                annotation=base_file_name,
                completion=symbol,
                kind=(sublime.KIND_ID_AMBIGUOUS, symbol_type, '')
            )

            if symbol not in unique_symbols:
                unique_symbols.append(symbol)
                self.items.append(completion_item)

        completions.set_completions(self.items)
        return completions

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
                if panel not in views:
                    views.append(panel)
        except Exception as e:
            print('No panel', e)

        # the last but not least are the open views
        for view in window.views():
            if view is not self.view:
                views.append(view)

        return views
