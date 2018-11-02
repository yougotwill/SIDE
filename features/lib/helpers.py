import os
import sublime


def get_word(view, point=None) -> str:
    ''' Gets the word under cursor or at the given point if provided. '''
    if not point:
        point = view.sel()[0].begin()
    return view.substr(view.word(point))


def defintion(word, view):
    ''' Return a list of locations for the given word. '''
    locations = _defintion_in_open_files(word) or _defintion_in_index(word)
    # filter by the extension
    filename, file_extension = os.path.splitext(view.file_name())
    return _locations_by_file_extension(locations, file_extension)
    
def _defintion_in_open_files(word):
    locations = sublime.active_window().lookup_symbol_in_open_files(word)
    return locations

def _defintion_in_index(word):
    locations = sublime.active_window().lookup_symbol_in_index(word)
    return locations

def _locations_by_file_extension(locations, extension):
    def _filter(location):
        filename, file_extension = os.path.splitext(location[0])
        return file_extension if file_extension == extension else False
    return list(filter(_filter, locations))