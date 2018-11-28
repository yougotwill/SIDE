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
     

class SideIgnoreWord(sublime_plugin.TextCommand):
    def run(self, edit, word):
        settings = sublime.load_settings("Preferences.sublime-settings")

        ignored_words = settings.get('ignored_words')
        if word not in ignored_words:
            ignored_words.append(word)
        settings.set('ignored_words', ignored_words)

        sublime.save_settings("Preferences.sublime-settings")