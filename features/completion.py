from SIDE.features.lib.helpers import _locations_by_file_extension
import os
import sublime
import sublime_plugin

def transform_to_location(file_path, region, symbol, symbol_type):
    ''' return a tuple (file_path, base_file_name, region, symbol, symbol_type) '''
    file_name = os.path.basename(file_path)
    base_file_name, file_extension = os.path.splitext(file_name)
    return (file_path, base_file_name, region, symbol, symbol_type)
    

class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):
        Side
        window = sublime.active_window()
        point = locations[0]
        views = window.views()

        symbols = []  # List[location]
        for view in views:
            locations = view.indexed_symbols()
            for location in locations:
                region, symbol = location
                scope_name = view.scope_name(region.begin())

                symbol_type = '[?]'
                if 'function' in scope_name and 'class' in scope_name:
                    symbol_type = '[m]'  # method
                elif 'class' in scope_name:
                    symbol_type = '[c]'  # class
                else:
                    symbol_type = '[f]'  # function
                
                location = transform_to_location(view.file_name(), region, symbol, symbol_type)
                symbols.append(location)

        _file_name, file_extension = os.path.splitext(self.view.file_name())
        symbols = _locations_by_file_extension(symbols, file_extension)

        completions = []

        for symbol_location in symbols:
            file_name, base_file_name, region, symbol, symbol_type = symbol_location
            completion_item = ["{}\t{}{}".format(symbol, base_file_name, symbol_type), "{}($1)$0".format(symbol)]
            completions.append(completion_item)

        return completions

