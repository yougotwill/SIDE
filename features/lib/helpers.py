import os
import sublime
import re


def get_word(view, point=None) -> str:
    ''' Gets the word under cursor or at the given point if provided. '''
    if not point:
        point = view.sel()[0].begin()
    return view.substr(view.word(point))

def get_function_name(view, start_point) -> str:
    ''' Get the function name when cursor is inside the parenthesies or when the cursor is on the function name. '''
    scope_name = view.scope_name(start_point)
    if 'variable.function' in scope_name or 'entity.name.function' in scope_name:
        return get_word(view)

    # if 'punctuation.section.arguments.begin' in scope_name or 'punctuation.section.group.begin' in scope_name:
    #     return ''

    open_bracket_region = view.find_by_class(start_point, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_LINE_END)
    while view.substr(open_bracket_region) is not '(':
        open_bracket_region = view.find_by_class(open_bracket_region, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_EMPTY_LINE)

    function_name_region = view.find_by_class(open_bracket_region, False, sublime.CLASS_WORD_START | sublime.CLASS_EMPTY_LINE)
    return view.substr(view.word(function_name_region))

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