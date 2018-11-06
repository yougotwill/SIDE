import sublime
import sublime_plugin

from random import randint

class SideAskQuestion(sublime_plugin.TextCommand):
    def run(self, edit):

        anwser = randint(0, 1)

        if anwser == 1:
            anwser = 'yes'
        else:
            anwser = 'no'
        self.view.show_popup("The anwser is {}".format(anwser), max_width=500)

     