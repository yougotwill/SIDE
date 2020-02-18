import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import find_symbols, find_references, debug
from SIDE.features.indexer import panel_state

last_view_id = None
cached_symbols = []
cached_references = []

class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        global last_view_id
        global cached_symbols
        global cached_references

        completions = sublime.CompletionList()

        # views is an array of view-s not including self.view
        views = self.sort_views_by_relevance()
        symbols = []

        current_view_symbols = find_symbols(self.view)

        if last_view_id != self.view.id():
            cached_symbols = find_symbols(self.view, views)

        symbols.extend(current_view_symbols)
        symbols.extend(cached_symbols)

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

        references = []

        current_view_references = find_references(self.view)
        if last_view_id != self.view.id():
            cached_references = find_references(self.view, views)

        references.extend(current_view_references)
        references.extend(cached_references)

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

        last_view_id = self.view.id()
        return completions

    def sort_views_by_relevance(self):
        """ Get a list of sorted views. This ensures we get the most relevant suggestions. """
        window = sublime.active_window()

        views = []
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
