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

        if 'function' in scope_name:
            self.handle_hover(point)

        if 'class' in scope_name or 'constructor' in scope_name:
            self.handle_hover(point, True)
        
    def handle_hover(self, point, is_class=False):
        word = get_word(self.view, point)
        locations = defintion(word, self.view)

        # display the reference count
        if len(locations) > 1:
            content = """
            <body id="side-hover" style="margin:0">
                <div style="color: color(var(--foreground) alpha(0.7)); padding: 7px;">
                    {} definitions
                </div>
            </body>""".format(len(locations))
            self.view.show_popup(content, point)

        # display the signiture, file origin, docs
        if len(locations) == 1:
            self.view.run_command('side_info_popup', {
                'location': locations[0], 
                'point': point,
                'is_class': is_class
            })
