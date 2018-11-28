import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word


def pluck_tuples(tuples, position):
    return list(map(lambda tuple: tuple[position] ,tuples))


class SideCodeAction(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.sel()[0]
        word = get_word(self.view, region).strip()

        actions = None
        action_commands = None
        if word:
            actions_and_commands = [
                ('Search Web', 'side_search_web')
            ]

            actions = pluck_tuples(actions_and_commands, 0)
            action_commands = pluck_tuples(actions_and_commands, 1)
        else:
            actions_and_commands = [
                ('Tell Joke', 'side_tell_joke'),
                ('Ask Yes/NO Question', 'side_ask_question'),
                ('Get Advice', 'side_advice')
            ] 

            actions = pluck_tuples(actions_and_commands, 0)
            action_commands = pluck_tuples(actions_and_commands, 1)     

        def on_select(index):
            if index > -1:
                self.view.run_command(action_commands[index])


        self.view.show_popup_menu(actions, on_select)
