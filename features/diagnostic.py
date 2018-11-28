import sublime
import sublime_plugin
import re

from SIDE.features.lib.helpers import debounce
from pyspellchecker.spellchecker import SpellChecker

spell = SpellChecker(distance=1)
MISSPELED_REGIONS = {} #window_id: [ misspeled_regions]

def underline_misspelled(view):
    window = sublime.active_window()
    symbols = view.indexed_symbols()
    references = view.indexed_references()

    # get only the references that are defined in project
    project_references = []
    for reference in references:
        region, symbol = reference
        symbol_in_project = window.lookup_symbol_in_open_files(symbol) or window.lookup_symbol_in_index(symbol)
        if len(symbol_in_project) > 0:
            project_references.append(reference)

    # only symbols and references in project will be spell checked
    symbols.extend(project_references)

    missspeled_regions = []
    for location in symbols:
        region, symbol = location

        # trim the _ form the symbol name
        symbol = symbol.strip('_')
        words = []
        if '_' in symbol:
            # handle cable case symbol names
            words = symbol.split('_')

        if re.match('^[A-Z][a-z]*', symbol): 
            # handle uppercase first camel case symbol names
            found_words = re.findall('[A-Z][a-z]*', symbol)
            for word in list(found_words):
                words.append(word.lower())

        elif re.match('[a-zA-Z][a-z]*', symbol):
            # handle lowercase first camel case symbol names
            found_words = re.findall('[a-zA-Z][a-z]*', symbol)
            for word in list(found_words):
                words.append(word.lower())

        misspelled = spell.unknown(words)

        settings = sublime.load_settings("Preferences.sublime-settings")
        ignored_words = settings.get('ignored_words', [])
        added_words = settings.get('added_words', [])

        for word in misspelled:
            if word not in ignored_words and word not in added_words:
                r = view.find(word, region.begin(), sublime.IGNORECASE)
                missspeled_regions.append(r)
 
    # underline misspelled words
    squiggly = sublime.DRAW_NO_FILL | sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_OUTLINE
    view.add_regions('side.diagnostic', missspeled_regions, 'markup.deleted', flags=squiggly)

    # this is used for code actions
    if not MISSPELED_REGIONS.get(window.id(), None):
        MISSPELED_REGIONS[window.id()] = []
    MISSPELED_REGIONS[window.id()] = missspeled_regions


class SideDiagnosticListener(sublime_plugin.ViewEventListener):
    def on_activated_async(self):
        self.spell_check_view()

    def on_modified_async(self): 
        self.spell_check_view()

    # this function is O(n^5) I think :D fun!!!
    # if you find a better way to handle this, you are welcome :)
    @debounce(0.4)
    def spell_check_view(self):
        underline_misspelled(self.view)

   