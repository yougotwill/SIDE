import sublime
import sublime_plugin


class SideToggleFindAll(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Preferences.sublime-settings")
        find_all = settings.get('side_toggle_find_all', False)

        if find_all:
            settings.set('side_toggle_find_all', False)
        else:
            settings.set('side_toggle_find_all', True)

        sublime.save_settings("Preferences.sublime-settings")
