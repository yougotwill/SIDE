import sublime
import sublime_plugin


class SideSpellCheck(sublime_plugin.TextCommand):
    def run(self, edit, region, suggested_word):
        # need to convert back to Region
        region = sublime.Region(region['begin'], region['end'])

        old_word = self.view.substr(region)
        is_first_letter_big = old_word.istitle()

        if is_first_letter_big:
            suggested_word = suggested_word.title()

        self.view.replace(edit, region, suggested_word)
     