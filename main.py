import sublime

from SIDE.features.show_signature import SideShowSignature, SideSignatureListener
from SIDE.features.definition import SideDefinition
from SIDE.features.hover import SideHover
from SIDE.features.signature_help import SideSignatureHelp
from SIDE.features.completion import SideCompletion
from SIDE.features.reference import SideReference
from SIDE.features.code_lens import SideCodeLens, SideToggleCodeLens
from SIDE.features.code_action import SideCodeAction
from SIDE.features.rename import SideRename
from SIDE.features.diagnostic import SideDiagnosticListener, spell
from SIDE.features.indexer import IndexerListener, SideIndexFileCommand, SideUpdateIndexPanelListener, index_view
from SIDE.features.highlight import SideHighlightListener, SideHiglightNextResult, SideHiglightPrevResult

from SIDE.features.commands.ask_question import SideAskQuestion
from SIDE.features.commands.search_web import SideSearchWeb
from SIDE.features.commands.tell_joke import SideTellJoke
from SIDE.features.commands.advice import SideAdvice
from SIDE.features.commands.spell_check import SideSpellCheck, SideIgnoreWord, SideAddWord
from SIDE.features.commands.toggle_find_all import SideToggleFindAll


def plugin_loaded():
    settings = sublime.load_settings("Preferences.sublime-settings")
    added_words = settings.get('added_words', [])
    spell.word_frequency.load_words(added_words)

    # index open views
    for view in sublime.active_window().views():
        index_view(view)
