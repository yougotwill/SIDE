import os
import sublime
import re
import linecache
from threading import Timer
from Default.history_list import get_jump_history_for_view

DEBUG = False


def debug(*args):
    if DEBUG:
        print(*args)


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


def highlight(view):
    """ Put a underline bellow current word. """
    word_regions = get_word_regions(view)     
    underline = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE

    if len(word_regions) > 0:
        view.add_regions('side_highlight', word_regions, scope="markup.inserted", flags=underline)
        settings = sublime.load_settings("Preferences.sublime-settings")
        find_all = settings.get('side_toggle_find_all', False)
        if find_all:
            view.set_status('side_selection_cound', "⧂ " + str(len(word_regions)))
        else:
            view.set_status('side_selection_cound', "⦾ " + str(len(word_regions)))
        return 

    view.erase_regions('side_highlight')
    view.erase_status('side_selection_cound')


def filter_regions_by_scope_name(regions, current_scope_name, view): 
    ''' Filter regions by current symbol '''
    function_match = []
    other_symbol_match = []

    for r in regions:
        scope_name = view.scope_name(r.begin())
        if is_function(scope_name):
            function_match.append(r)
        elif is_import(scope_name):
            # we dont know wether the import word is a function or some other type
            # so we assign it to both arrays
            function_match.append(r)
            other_symbol_match.append(r)
        else:
            other_symbol_match.append(r)

    if is_function(current_scope_name):
        return function_match
    if is_import(current_scope_name):
        result = []
        regions = function_match + other_symbol_match
        for r in regions:
            if r not in result:
                result.append(r)
        return result
    else:
        return other_symbol_match


def filter_regions_by_region(regions, region): 
    ''' Get only the regions contained it a region '''
    match = []
    if region is not None:
        for r in regions:
            if region.contains(r):
                match.append(r)
    return match

def get_region_between_symbols(point, symbols, view):
    ''' Return a Region or None'''
    # type List[region]
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
        open_view(location, current_view, force_open=True)

    def _on_change(index):                    
        location = quick_panel['on_select'][index]
        open_view(location, current_view, sublime.ENCODED_POSITION | sublime.TRANSIENT, force_open=True)

    window.show_quick_panel(
        quick_panel['labels'],
        _on_done,
        on_highlight=_on_change
    )

def is_import(scope_name):
    if 'meta.statement.import' in scope_name or \
       'meta.use' in scope_name or \
       'meta.import' in scope_name:
        return True
    else: 
        return False

def is_function(scope_name):
    if 'variable.function' in scope_name or \
       'entity.name.function' in scope_name or \
       'variable.annotation.function' in scope_name or \
       'punctuation.section.group.begin' in scope_name or \
       'punctuation.section.arguments.begin' in scope_name or \
       'support.function' in scope_name:
        return True
    else: 
        return False

def is_class(scope_name):
    if 'entity.name.class' in scope_name or \
       'support.class' in scope_name:
        return True
    else: 
        return False

def is_tag(scope_name):
    if 'meta.tag' in scope_name:
        return True
    return False

def is_trait(scope_name):
    if 'entity.other.inherited-class' in scope_name or \
       'entity.name.trait' in scope_name:
        return True
    return False

def open_view(location, current_view, flags=sublime.ENCODED_POSITION, force_open=False):
    ''' Opens a view with the cursor at the specified location. '''
    window = sublime.active_window()

    file_path, _rel_file_path, row_col = location
    new_row, new_col = row_col

    # save to jump back history
    if not current_view.settings().get('is_widget'):
        get_jump_history_for_view(current_view).push_selection(current_view)

    v = window.find_open_file(file_path)
    # force_open fixes freeze when goto definition is triggered
    # so don't touch it :D
    if v is not None and not force_open:
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
    absolute_file_name = view.file_name()
    if not absolute_file_name:
        debug('No file_name for the current view in reference()')
        return []
    filename, file_extension = os.path.splitext(absolute_file_name)
    return _locations_by_file_extension(locations, file_extension)
    
def _reference_in_open_files(word):
    locations = sublime.active_window().lookup_references_in_open_files(word)
    return locations

def _reference_in_index(word):
    locations = sublime.active_window().lookup_references_in_index(word)
    return locations

def find_references(current_view, views=None):
    ''' Return a list of references locations [(file_path, base_file_name, region, symbol, symbol_type)]. '''
    references = []  # List[location]
    if views is not None:
        for view in views:
            locations = view.indexed_references()
            symbols_in_view = _find_symbols_for_view(view, locations)
            references.extend(symbols_in_view)
    else:
        locations = current_view.indexed_references()
        symbols_in_view = _find_symbols_for_view(current_view)
        references.extend(symbols_in_view)

    absolute_file_name = current_view.file_name()
    if not absolute_file_name:
        debug('No file_name for the current view')
        return []
    _file_name, file_extension = os.path.splitext(absolute_file_name)
    references = _locations_by_file_extension(references, file_extension)
    return references

def get_symbol_type(scope_name):
    symbol_type = '#'
    if 'class' in scope_name and 'function' in scope_name:
        symbol_type = 'μ'
    elif 'function' in scope_name:
        symbol_type = 'λ'  # function
    elif 'class' in scope_name:
        symbol_type = '⚼'  # class
    elif 'struct' in scope_name or 'impl' in scope_name:
        symbol_type = '□'  # struct
    elif 'trait' in scope_name:
        symbol_type = '◳'
    return symbol_type

def find_symbols(current_view, views=None):
    ''' Return a list of symbol locations [(file_path, base_file_name, region, symbol, symbol_type)]. '''
    symbols = []  # List[location]
    if views is not None:
        for view in views:
            locations = view.indexed_symbols()
            symbols_in_view = _find_symbols_for_view(view, locations)
            symbols.extend(symbols_in_view)
    else:
        locations = current_view.indexed_symbols()
        symbols_in_view = _find_symbols_for_view(current_view, locations)
        symbols.extend(symbols_in_view)
            
    absolute_file_name = current_view.file_name()
    if not absolute_file_name:
        debug('No file_name for the current view')
        return []
    _file_name, file_extension = os.path.splitext(absolute_file_name)
    symbols = _locations_by_file_extension(symbols, file_extension)
    return symbols


def _find_symbols_for_view(view, locations):
        symbols = []  # List[location]
        for location in locations:
            region, symbol = location
            scope_name = view.scope_name(region.begin())
            symbol_type = get_symbol_type(scope_name)

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

def toggle_dash_if_tag(tag, view):
    word_separators = view.settings().get('word_separators', "")
    if tag and '-' in word_separators:
        word_separators = word_separators.replace('-', '')
        view.settings().set('word_separators', word_separators)
    elif not tag and '-' not in word_separators:
        word_separators += '-'
        view.settings().set('word_separators', word_separators)

def get_word_regions(view):
    ''' Returns regions based on the current scope name.
        If it is a function or import, return word regions from the whole file,
        Else return word regions between symbols.'''
    sel = view.sel()
    if len(sel) < 1:
        return []

    point = sel[0].begin()
    scope_name = view.scope_name(point)

    # match tag names that have a - between
    tag = is_tag(scope_name)
    toggle_dash_if_tag(tag, view)

    word_region = view.word(point)

    # flags
    accessor = is_accessor(view, word_region)
    function = is_function(scope_name)
    import_scope = is_import(scope_name)

    word = view.substr(word_region).strip().strip('(').strip(')')
    if not word:
        return []

    word_regions = view.find_all(r"\b{}\b".format(word))
    
    settings = sublime.load_settings("Preferences.sublime-settings")
    find_all = settings.get('side_toggle_find_all', False)
    if find_all or function or import_scope:
        # select from file start to file end 
        between_symbols_region = sublime.Region(0, view.size())
    else:
        # filter between symbols
        symbols = find_symbols(view)
        between_symbols_region = get_region_between_symbols(point, symbols, view)
    if between_symbols_region:
        word_regions = filter_regions_by_region(word_regions, between_symbols_region)

    # filter by accessors
    if not function:
        word_regions = list(filter(lambda r: is_accessor(view, r) == accessor, word_regions))  

    word_regions = filter_regions_by_scope_name(word_regions, scope_name, view) 

    # filter out strings
    word_regions_no_strings = list(filter(lambda r: 'string.quoted' not in view.scope_name(r.begin()), word_regions))  
    regions_under_cursor = filter_regions_by_region(word_regions_no_strings, word_region)

    # this is used to smatly select strings. I believe this will be a brain fuck in the future to understand
    if len(word_regions_no_strings) > 0 and len(regions_under_cursor) > 0:
        return word_regions_no_strings
    # useful for debugging
    # if between_symbols_region is not None:
    #     view.add_regions('function', [between_symbols_region], 'comment', flags=sublime.DRAW_OUTLINED)
    # view.add_regions('word', word_regions, 'string', flags=sublime.DRAW_OUTLINED)        
    return word_regions

def is_accessor(view, word_region):
    '''  Check if the current word has an is_accessor like a . or > before it '''
    point_before_word = word_region.begin() - 1
    scope_before_region = view.scope_name(point_before_word)
    accessor = False
    if 'punctuation.accessor' in scope_before_region:
        accessor = True
    return accessor        

def get_word(view, point=None) -> str:
    ''' Gets the word under cursor or at the given point if provided. '''
    if not point:
        point = view.sel()[0].begin()
    return view.substr(view.word(point))


def get_function_name(view, start_point) -> str:
    ''' Get the function name when cursor is inside the parenthesis or when the cursor is on the function name. '''
    scope_name = view.scope_name(start_point)
    if is_function(scope_name) or is_class(scope_name):
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
        if file_extension == extension:
            return True
        else:
            return False
    return list(filter(_filter, locations))
