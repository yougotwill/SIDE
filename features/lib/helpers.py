import os
import sublime


def get_word(view, point=None):
    if not point:
        point = view.sel()[0].begin()
    return view.substr(view.word(point))

def defintion_in_open_files(word):
    locations = sublime.active_window().lookup_symbol_in_open_files(word)
    return locations

def defintion(word):
    locations = sublime.active_window().lookup_symbol_in_index(word)
    return locations

def locations_by_file_extension(locations, extension):
    def _filter(location):
        filename, file_extension = os.path.splitext(location[0])
        return file_extension if file_extension == extension else False

    return list(filter(_filter, locations))