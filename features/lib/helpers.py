import os
import sublime
import re
import linecache
from threading import Timer


history = {} # type: Dict[window_id, bookmarks]


def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator


def filter_regions_by_scope_name(regions, current_scope_name, view): 
    ''' Filter regions by current symbol '''
    function_match = []
    other_symbol_match = []

    for r in regions:
        scope_name = view.scope_name(r.begin())
        if is_function(scope_name):
            function_match.append(r)
        else:
            other_symbol_match.append(r)
    if is_function(current_scope_name):
        return function_match
    else:
        return other_symbol_match


def filter_regions_by_region(regions, region): 
    ''' Return a list of regions '''
    match = []
    if region is not None:
        for r in regions:
            if region.contains(r):
                match.append(r)
    return match

def get_region_between_symbols(point, symbols, view):
    ''' Return a Region or None'''
    # type List[reigion]
    regions = list(map(lambda l: l[2], symbols))
    for index, region in enumerate(regions):          
        # check to see if the point is between two symbols        
        if index == len(regions) - 1:
            a = region.begin()
            b = view.size()
            r = sublime.Region(a, b)
            if r.contains(point):
                return r
        else:
            a = region.begin()
            nexe_region = regions[index+1]
            b = nexe_region.begin()
            r = sublime.Region(a, b)
            if r.contains(point):
                return r    
    return None


def scroll_to_not_visible_region(regions, view):
    visible = view.visible_region()
    first_region = regions[0]
    last_region = regions[-1]

    is_first_visible = visible.contains(first_region)
    is_last_visible = visible.contains(last_region)

    if not is_first_visible and not is_last_visible:
        view.show_at_center(last_region)
    elif not is_last_visible:
        view.show_at_center(last_region)
    elif not is_first_visible:
        view.show_at_center(first_region)


def chose_one_location_from_many(locations, current_view) -> None:
    window = sublime.active_window()

    quick_panel = {
        'labels': [],
        'on_select': []
    }

    for location in locations:
        file_path, relative_file_path, row_col = location
        row, col = row_col
        quick_panel['labels'].append("{}:{}:{}".format(relative_file_path, row, col))
        quick_panel['on_select'].append(location)
    
    def _on_done(index):
        if index == -1:
            window.focus_view(current_view)
            return 
        location =  quick_panel['on_select'][index]
        open_view(location, current_view)

    def _on_change(index):                    
        location = quick_panel['on_select'][index]
        open_view(location, current_view, sublime.ENCODED_POSITION | sublime.TRANSIENT, record_history=False)

    window.show_quick_panel(
        quick_panel['labels'],
        _on_done,
        on_highlight=_on_change
    )


def is_function(scope_name):
    if 'variable.function' in scope_name or \
       'entity.name.function' in scope_name or \
       'support.function' in scope_name:
        return True
    else: 
        return False

def is_class(scope_name):
    if 'entity.name.class' in scope_name or \
       'constructor' in scope_name or \
       'support.class' in scope_name:
        return True
    else: 
        return False


def open_view(location, current_view, flags=sublime.ENCODED_POSITION, record_history=True):
    ''' Opens a view with the cursor at the specefied location. And save it to the jump back history. '''
    window = sublime.active_window()
    old_cursor_pos = current_view.sel()[0].begin()
    old_row, old_col = current_view.rowcol(old_cursor_pos)

    bookmark = (current_view.file_name(), (old_row, old_col))

    file_path, _rel_file_path, row_col = location
    new_row, new_col = row_col
    # save bookmark 
    if record_history and (old_row != new_row or old_col != new_col):
        id = window.id()
        bookmarks = history.get(id, [])
        bookmarks.append(bookmark)
        history[id] = bookmarks
    # open location
    v = window.find_open_file(file_path)
    if v is not None:
        window.focus_view(v)
        point = v.text_point(new_row - 1, new_col - 1)
        sel = v.sel()
        sel.clear()
        sel.add(point)
        v.show_at_center(point)
    else:
        window.open_file("{}:{}:{}".format(file_path, new_row, new_col), flags)


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


def reference(word, view, all=True):
    if all:
        locations = _reference_in_index(word)
    else: 
        locations = _reference_in_open_files(word) or _reference_in_index(word)
    # filter by the extension
    filename, file_extension = os.path.splitext(view.file_name())
    return _locations_by_file_extension(locations, file_extension)
    
def _reference_in_open_files(word):
    locations = sublime.active_window().lookup_references_in_open_files(word)
    return locations

def _reference_in_index(word):
    locations = sublime.active_window().lookup_references_in_index(word)
    return locations


def find_symbols(current_view, views=None):
    ''' Return a list of symbol locations [(file_path, base_file_name, region, symbol, symbol_type)]. '''
    symbols = []  # List[location]
    if views is not None:
        for view in views:
            symbols_in_view = _find_symbols_for_view(view)
            symbols.extend(symbols_in_view)
    else:
        symbols_in_view = _find_symbols_for_view(current_view)
        symbols.extend(symbols_in_view)
            
    _file_name, file_extension = os.path.splitext(current_view.file_name())
    symbols = _locations_by_file_extension(symbols, file_extension)
    return symbols

def _find_symbols_for_view(view):
        locations = view.indexed_symbols()

        symbols = []  # List[location]
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
            elif 'struct' in scope_name or 'impl' in scope_name:
                symbol_type = '[s]'  # struct

            
            location = _transform_to_location(view.file_name(), region, symbol, symbol_type)
            symbols.append(location)

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
        'support.function' in scope_name or \
        'entity.name.function' in scope_name or \
        'entity.name.class' in scope_name or \
        'support.class' in scope_name:
        return get_word(view)

    if 'punctuation.section.arguments.begin' in scope_name or 'punctuation.section.group.begin' in scope_name:
        return ''

    open_bracket_region = view.find_by_class(start_point, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_LINE_END)

    while view.substr(open_bracket_region) is not '(' and open_bracket_region > 0:
        open_bracket_region = view.find_by_class(open_bracket_region, False, sublime.CLASS_PUNCTUATION_START | sublime.CLASS_EMPTY_LINE)

    if open_bracket_region is 0:
        return ''

    function_name_region = view.find_by_class(open_bracket_region, False, sublime.CLASS_WORD_START | sublime.CLASS_EMPTY_LINE | sublime.CLASS_LINE_START)
    return view.substr(view.word(function_name_region))


def definition(word, view):
    ''' Return a list of locations for the given word. '''
    locations = _definition_in_open_files(word) or _definition_in_index(word)
    # filter by the extension
    filename, file_extension = os.path.splitext(view.file_name())
    return _locations_by_file_extension(locations, file_extension)
    
def _definition_in_open_files(word):
    locations = sublime.active_window().lookup_symbol_in_open_files(word)
    return locations

def _definition_in_index(word):
    locations = sublime.active_window().lookup_symbol_in_index(word)
    return locations


def _locations_by_file_extension(locations, extension):
    def _filter(location):
        filename, file_extension = os.path.splitext(location[0])
        if file_extension == extension or extension == '.html' or extension == '.ts' or extension == '.js' or extension == '.vue':
            return True
        else:
            return False
    return list(filter(_filter, locations))
