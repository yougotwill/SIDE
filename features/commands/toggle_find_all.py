import sublime
import sublime_plugin

from SIDE.features.lib.helpers import highlight


class SideToggleFindAll(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Preferences.sublime-settings")
        find_all = settings.get('side_toggle_find_all', False)
                
        if find_all:
            self.view.set_status('side_selection_cound', "⦾")
            settings.set('side_toggle_find_all', False)
        else:
            self.view.set_status('side_selection_cound', "⧂")
            settings.set('side_toggle_find_all', True)
        sublime.save_settings("Preferences.sublime-settings")
        # update the higlight
        highlight(self.view)
