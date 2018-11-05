import os
import sublime
import re
import linecache

history = {} # type: Dict[window_id, bookmarks]

def open_view(location, current_view, flags=sublime.ENCODED_POSITION):
    ''' Returns a view with the cursor at the specefied location. And save it to the jump back history. '''
    window = sublime.active_window()
    old_cursor_pos = current_view.sel()[0].begin()
    old_row, old_col = current_view.rowcol(old_cursor_pos)
    # normalize row and column
    old_row += 1
    old_col += 1
    bookmark = (current_view.file_name(), (old_row, old_col))

    file_path, _rel_file_path, row_col = location
    new_row, new_col = row_col
    # save bookmark 
    if old_row != new_row or old_col != new_col:
        id = window.id()
        bookmarks = history.get(id, [])
        bookmarks.append(bookmark)
        history[id] = bookmarks
    # open location
    return window.open_file("{}:{}:{}".format(file_path, new_row, new_col), flags)

def get_project_path(window):
    """
    Returns the first project folder or the parent folder of the active view
    """
    if len(window.folders()):
        folder_paths = window.folders()
        return folder_paths[0]
    else:
        view = window.active_view()
        if view:
            filename = view.file_name()
            if filename:
                project_path = os.path.dirname(filename)
                return project_path


def reference(word, view):
    locations = _reference_in_index(word)
    # filter by the extension
    filename, file_extension = os.path.splitext(view.file_name())
    return _locations_by_file_extension(locations, file_extension)
    
def _reference_in_index(word):
    locations = sublime.active_window().lookup_references_in_index(word)
    return locations


def find_symbols(current_view, views):
    ''' Return a list of symbol locations [(file_path, base_file_name, region, symbol, symbol_type)]. '''
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
            elif 'function' in scope_name:
                symbol_type = '[f]'  # function
            
            location = _transform_to_location(view.file_name(), region, symbol, symbol_type)
            symbols.append(location)
            
    _file_name, file_extension = os.path.splitext(current_view.file_name())
    symbols = _locations_by_file_extension(symbols, file_extension)
    return symbols

def _transform_to_location(file_path, region, symbol, symbol_type):
    ''' return a tuple (file_path, base_file_name, region, symbol, symbol_type) '''
    file_name = os.path.basename(file_path)
    base_file_name, file_extension = os.path.splitext(file_name)
    return (file_path, base_file_name, region, symbol, symbol_type)

def get_line(view, file_name, row) -> str:
    ''' 
    Get the line from the buffer or if not from linecache.
    '''
    is_in_buffer = view.file_name() == file_name

    line = ''
    if is_in_buffer:
        # get from buffer
        # normalize the row
        point = view.text_point(row - 1, 0)
        return view.substr(view.line(point))
    else: 
        # get from linecache
        return linecache.getline(file_name, row)

        

def get_word(view, point=None) -> str:
    ''' Gets the word under cursor or at the given point if provided. '''
    if not point:
        point = view.sel()[0].begin()
    return view.substr(view.word(point))

def get_function_name(view, start_point) -> str:
    ''' Get the function name when cursor is inside the parenthesies or when the cursor is on the function name. '''
    scope_name = view.scope_name(start_point)
    if 'variable.function' in scope_name or \
        'entity.name.function' in scope_name or \
        'entity.name.class' in scope_name or \
        'support.class' in scope_name:
        return get_word(view)

    if 'punctuation.section.arguments.begin' in scope_name or 'punctuation.section.group.begin' in scope_name:
        return ''

    open_bracket_region = view.find_by_class(start_point, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_LINE_END)

    while view.substr(open_bracket_region) is not '(' and open_bracket_region is not 0:
        open_bracket_region = view.find_by_class(open_bracket_region, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_EMPTY_LINE)

    if open_bracket_region is 0:
        return ''

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