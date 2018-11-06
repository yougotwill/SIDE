import sublime
import sublime_plugin

from random import randint

class SideAskQuestion(sublime_plugin.TextCommand):
    def run(self, edit):

        anwser = randint(0, 100)

        if anwser > 50:
            anwser = 'yes'
        elif anwser == 42:
            anwser = '42'
        else:
            anwser = 'no'
            
        self.view.show_popup("The anwser to your question is {}".format(anwser), max_width=500)

     