import sublime
import sublime_plugin

from SIDE.features.lib.helpers import get_word
from SIDE.features.diagnostic import MISSPELED_REGIONS, spell

def pluck_tuples(tuples, position):
    return list(map(lambda tuple: tuple[position] ,tuples))

def in_diagnostic_regions(point) -> sublime.Region:
    ''' Return the diagnostic region containing the point, or None. '''
    window = sublime.active_window()
    misspeled_regions = MISSPELED_REGIONS.get(window.id())
    for region in misspeled_regions:
        if region.contains(point):
            return region
    return None

class SideCodeAction(sublime_plugin.TextCommand):
    def run(self, edit):
        region = self.view.sel()[0]
        point = region.begin()

        diagnostic_region = in_diagnostic_regions(point)

        # search the whole word
        word = get_word(self.view, region).strip()

        actions = None
        action_commands = None
        if word:
            actions_and_commands = [
                ('Search Web', 'side_search_web')
            ]

            if diagnostic_region is not None:
                actions_and_commands.append(('-', None))
                word = self.view.substr(diagnostic_region).lower()

                corrections = spell.candidates(word)
                for w in corrections:
                    actions_and_commands.append((w, 'side_spell_check'))
                print('word', word)
                print('corrections', corrections)
                actions_and_commands.append(('-', None))
                actions_and_commands.append(('Ignore Word', 'side_ignore_word'))

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
