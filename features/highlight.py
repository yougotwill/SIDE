from SIDE.features.lib.helpers import debounce, get_word_regions
import sublime
import sublime_plugin

# from dsadasd import sel

# class Sel:
#     def sel():
#         self.sel()
#         sel()
#         self.sel.sel()
#         sel
#         sel
#         sel

#     def sel():
#         self.sel()
#         sel()
#         self.sel.sel()
#         sel


class SideHighlightListener(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        self.handle_selection_modified()

    @debounce(0.3)
    def handle_selection_modified(self):
        word_regions = get_word_regions(self.view)        
        underline = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE

        if len(word_regions) > 0:
            self.view.add_regions('side_highlight', word_regions, scope="markup.inserted", flags=underline)
            self.view.set_status('side_selection_cound', "⦾ " + str(len(word_regions)))
            return 

        self.view.erase_regions('side_highlight')
        self.view.erase_status('side_selection_cound')
