from SIDE.features.lib.helpers import _locations_by_file_extension
import os
import sublime
import sublime_plugin

def transform_to_location(file_path, symbol, region):
    file_name = os.path.basename(file_path)
    base_file_name, file_extension = os.path.splitext(file_name)
    return (file_path, base_file_name, region, symbol)
    

class SideCompletion(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix, locations):

        window = sublime.active_window()
        point = locations[0]
        views = window.views()
        


        symbols = []  # List[location]
        for view in views:
            locations = view.indexed_symbols()
            for location in locations:
                region, symbol = location

                location = transform_to_location(view.file_name(), symbol, region)
                symbols.append(location)

        filename, file_extension = os.path.splitext(self.view.file_name())
        print("filename", filename)
        symbols = _locations_by_file_extension(symbols, file_extension)
        print(symbols)

        completions = []
        for symbol_location in symbols:
            file_name, base_file_name, region, symbol = symbol_location
            completion_item = ["{}\t{}".format(symbol, base_file_name), "{}($1)$0".format(symbol)]
            completions.append(completion_item)

        return completions

