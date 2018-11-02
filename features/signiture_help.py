import sublime
import sublime_plugin


class SideSignitureHelp(sublime_plugin.ViewEventListener):
    def on_modified_async(self):
        point = self.view.sel()[0].begin()
        last_char = self.view.substr(point - 1)

        if last_char in ['(', ',']:
            self.show_signiture_help(point)
        else:
            self.hide_signiture_help()

    def show_signiture_help(self, point):
        self.view.show_popup('content', sublime.HIDE_ON_MOUSE_MOVE_AWAY, location=point, max_width=700)
    
    def hide_signiture_help(self):
        if self.view.is_popup_visible():
            self.view.hide_popup()
