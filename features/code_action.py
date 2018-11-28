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

        
        word = get_word(self.view, region).strip()

        actions = None
        action_commands = None
        if word:
            # actions_and_commands ('Label', 'command', optional 'args')
            actions_and_commands = [
                ('Search Web', 'side_search_web')
            ]

            # add spell check if in diagnostics region
            if diagnostic_region is not None:
                # add divider at the beginning
                actions_and_commands.append(('-', None))

                misspelled_word = self.view.substr(diagnostic_region).lower()

                corrections = spell.candidates(misspelled_word)
                for suggested_word in corrections:
                    arguments = {
                        'region': { 'begin':diagnostic_region.begin(), 'end': diagnostic_region.end() },
                        'suggested_word': suggested_word
                    }
                    actions_and_commands.append((suggested_word, 'side_spell_check', arguments))

                # add divider at the end
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
                # if the length of the tuple is 3, than the 3rd item are the arguments
                if len(actions_and_commands[index]) == 3:
                    arguments = actions_and_commands[index][2]
                    self.view.run_command(action_commands[index], arguments)
                else:
                    self.view.run_command(action_commands[index])



        self.view.show_popup_menu(actions, on_select)
