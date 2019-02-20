import sublime
import sublime_plugin

from SIDE.features.lib.helpers import scroll_to_not_visible_region, get_word_regions


class SideRename(sublime_plugin.TextCommand):
    def run(self, edit):
        word_regions = get_word_regions(self.view)        

        sel = self.view.sel()
        if len(sel) > 1:
            scroll_to_not_visible_region(word_regions, self.view)

        if len(word_regions) > 0:
            sel.clear()
            sel.add_all(word_regions)


       