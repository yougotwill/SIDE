from SIDE.features.lib.helpers import get_function_name, defintion
import sublime
import sublime_plugin


class SideSignitureHelp(sublime_plugin.ViewEventListener):
    def on_modified_async(self):
        point = self.view.sel()[0].begin()
        last_char = self.view.substr(point - 1)

        if last_char in ['(', ',']:
            word = get_function_name(self.view, point)
            self.show_signiture_help(point, word)
        else:
            self.hide_signiture_help()

    def show_signiture_help(self, point, word):
        locations = defintion(word, self.view)

        self.view.run_command('side_show_signiture', {
            'locations': locations, 
            'point': point
        })

    
    def hide_signiture_help(self):
        if self.view.is_popup_visible():
            self.view.hide_popup()