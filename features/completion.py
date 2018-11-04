import os
import sublime
import sublime_plugin

from SIDE.features.lib.helpers import symbols_for_view_in_views


class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        window = sublime.active_window()
        point = locations[0]
        views = window.views()

        symbols = symbols_for_view_in_views(self.view, views)

        completions = []

        for symbol_location in symbols:
            file_name, base_file_name, region, symbol, symbol_type = symbol_location
            completion_item = ["{}\t{}{}".format(symbol, base_file_name, symbol_type), "{}($1)$0".format(symbol)]
            completions.append(completion_item)

        return (completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS)

