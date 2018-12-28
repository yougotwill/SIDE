import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import definition


# key will be the panel_name
# holding an set of view ids
# if the set is empty the panel will be destroyed
panel_state = {} 
DEBUG = True

def debug(*args):
    if DEBUG:
        print(*args)

class IndexerListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        global panel_state
        window = sublime.active_window()
        debug('on_load', self.view.id())
        # select all unique references
        references = self.view.indexed_references()
        words = list(set(map(lambda x: x[1], references)))

        files_to_index = set()
        for word in words:
            definitions = definition(word, self.view)
            if len(definitions) == 1:
                # add the apsolute file name
                absolute_file_path = definitions[0][0]
                relative_file_path = definitions[0][1]

                if not window.find_open_file(absolute_file_path):
                    debug('added [ {} ] files_to_index because of symbol {}'.format(relative_file_path, word))
                    files_to_index.add((absolute_file_path, relative_file_path))

        # indexing
        for absolute_file_path, panel_name in files_to_index:
            with open(absolute_file_path) as file:  
                panel = window.find_output_panel(panel_name)
                # if it is indexed continue
                if panel:
                    # keep track of it
                    debug("[ {} ] panel already exist".format(panel_name))
                    panel_state[panel_name].add(self.view.id())
                    debug('panel_state when panel exist', panel_state)
                    continue
                # else index it
                content = file.read() 
                debug('read file')

                # trigger index command
                self.view.run_command('side_index_file', {
                        'content': content,
                        'panel_name': panel_name
                    })

                # keep track of it
                if not panel_state.get(panel_name):
                    debug('create state for [ {} ]'.format(panel_name))
                    panel_state[panel_name] = set()
                panel_state[panel_name].add(self.view.id())
                debug('panel_state after creating state', panel_state)


    def on_pre_close(self):
        global panel_state
        debug('on_closed', self.view.id())
        debug('panel_state before for loop', panel_state)

        for panel_name in panel_state:
            id = self.view.id()
            if id in panel_state[panel_name]:
                debug('remove view {}'.format(id))
                panel_state[panel_name].remove(id)

            if len(panel_state[panel_name]) == 0:
                debug('destroing panel [ {} ]'.format(panel_name))
                window = sublime.active_window()
                window.destroy_output_panel(panel_name)
        debug('panel_state after for loop', panel_state)



class SideIndexFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, content, panel_name):
        debug('command SideIndexFileCommand called')
        window = sublime.active_window()
        panel = window.create_output_panel(panel_name)
        syntax = self.view.settings().get('syntax')
        panel.assign_syntax(syntax)
        debug('panel [ {} ] created'.format(panel_name))
        panel.insert(edit, 0, content)

