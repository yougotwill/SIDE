import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import get_word, defintion


class SideHover(sublime_plugin.ViewEventListener):
    def on_hover(self, point, hover_zone):
        scope_name = self.view.scope_name(point)
        # not hovering over text
        if hover_zone != sublime.HOVER_TEXT:
            return

        if 'function' in scope_name or 'class' in scope_name or 'constructor' in scope_name:
            self.handle_hover(point)

    def handle_hover(self, point, is_class=False):
        word = get_word(self.view, point)
        locations = defintion(word, self.view)

        self.view.run_command('side_show_signiture', {
            'locations': locations, 
            'point': point
        })
