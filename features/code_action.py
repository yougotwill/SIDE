import sublime
import sublime_plugin


class SideCodeAction(sublime_plugin.TextCommand):
    def run(self, edit):
        actions = [
            'Search Web', 
            'Tell Joke', 
            'Ask Yes/NO Question' 
        ]

        action_commands = [
            'side_search_web',
            'side_tell_joke',
            'side_ask_question'
        ]

        def on_select(index):
            if index > -1:
                self.view.run_command(action_commands[index])


        self.view.show_popup_menu(actions, on_select)
