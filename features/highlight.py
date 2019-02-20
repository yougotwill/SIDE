from SIDE.features.lib.helpers import debounce, get_word_regions, highlight
import sublime
import sublime_plugin


class SideHighlightListener(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        self.handle_selection_modified()

    @debounce(0.3)
    def handle_selection_modified(self):
        highlight(self.view)


def show_highlighted_word(step, view):
        word_regions = view.get_regions('side_highlight')

        # return if no point
        point = view.sel()[0].begin()
        if point is None:
            return

        # get the current region containing the point
        current_region = list(filter(lambda r: r.contains(point), word_regions))
        if len(current_region) == 1:
            current_region = current_region[0]
        else:
            return

        # find the index and calculate the next one
        index = word_regions.index(current_region) 
        index += step

        # reset the index beck to 0/end, if it goes bellow 0 or above end
        if index < 0:
            index = len(word_regions) - 1

        if index >= len(word_regions):
            index = 0

        sel = view.sel()
        sel.clear()
        sel.add_all([word_regions[index].end()])
        view.show_at_center(word_regions[index])


class SideHiglightNextResult(sublime_plugin.TextCommand):
    def run(self, edit):
        show_highlighted_word(1, self.view)


class SideHiglightPrevResult(sublime_plugin.TextCommand):
    def run(self, edit):
        show_highlighted_word(-1, self.view)

    