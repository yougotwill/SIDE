import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word


class SideCodeAction(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.sel()[0]
        word = get_word(self.view, region).strip()

        actions = None
        action_commands = None
        if word:
            actions = [
                'Search Web', 
            ]
            action_commands = [
                'side_search_web'
            ]
        else:
            actions = [
                'Tell Joke', 
                'Ask Yes/NO Question',
                'Get Advice'
            ]
            action_commands = [
                'side_tell_joke',
                'side_ask_question',
                'side_advice'
            ]        

        def on_select(index):
            if index > -1:
                self.view.run_command(action_commands[index])


        self.view.show_popup_menu(actions, on_select)
