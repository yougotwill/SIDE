from SIDE.features.lib.helpers import debounce, get_word_regions, highlight
import sublime
import sublime_plugin


class SideHighlightListener(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        self.handle_selection_modified()

    @debounce(0.3)
    def handle_selection_modified(self):
        highlight(self.view)
