from sublime import Region
import sublime
import sublime_plugin
import os

from SIDE.features.lib.helpers import definition, debug


# key will be the panel_name, witch is the absolute file name
# holding an set of view ids
# if the set is empty the panel will be destroyed
panel_state = {}

# Here is a brief explanation. Imaine we have file, A, B, C, D
# And that file A, have some functions defined in C, which are used in A
# And that file B, have some functiond defined in C and D, which are used in B 
#
# The panel_state for that case would look like this: 
# {
#   "C" : ["A", "B"],
#   "D" : ["B"]
# }
# 
# Under the hood, two output panels are created for files C, D
# We grab of all the indexed simbols from the output panels.
# And later in completions show those symbols.
# 
# If file B is closed, the panels_state would look like this:
# {
#   "C": ["A"]
# }
# 
# The "D" panel was destoryed because there were no files associated to it.
# Similary if we closed the file A, 
# The "C" panel would be destored, because there we no more files associated with it. 

def index_view(view):
    debug('index view', view.id())
    window = sublime.active_window()

    # select all unique references, and extreact the words
    references = view.indexed_references()
    words = list(set(map(lambda x: x[1], references)))

    files_to_index = set()
    for word in words:
        definitions = definition(word, view)
        if len(definitions) == 1:
            # add the absolute file name
            absolute_file_path = definitions[0][0]

            # don't add to index if they are already open
            if not window.find_open_file(absolute_file_path):
                debug('added file [ {} ] for indexing for symbol {}'.format(absolute_file_path, word))
                files_to_index.add(absolute_file_path)

    # indexing
    for absolute_file_path in files_to_index:
        # alias the panel name to be the apsolute file name
        panel_name = absolute_file_path

        with open(absolute_file_path) as file:  
            panel = window.find_output_panel(panel_name)

            # if it is indexed continue
            if panel:
                # keep track of it
                panel_state[panel_name].add(view.id())
                debug("[ {} ] panel already exist".format(panel_name))
                debug('panel_state when panel exist', panel_state)
                continue

            # else index it
            content = file.read() 
            view.run_command('side_index_file', {
                    'content': content,
                    'panel_name': panel_name
                })

            # keep track of it
            if not panel_state.get(panel_name):
                debug('create state for [ {} ]'.format(panel_name))
                panel_state[panel_name] = set()
            panel_state[panel_name].add(view.id())
            debug('panel_state after creating state', panel_state)


class IndexerListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        index_view(self.view)

    def on_pre_close(self):
        global panel_state
        id = self.view.id()
        debug('on_closed', id)
        debug('panel_state before for loop', panel_state)

        for panel_name in list(panel_state):
            if id in panel_state[panel_name]:
                debug('remove view {}'.format(id))
                panel_state[panel_name].remove(id)

            if len(panel_state[panel_name]) == 0:
                debug('destroying panel [ {} ]'.format(panel_name))
                window = sublime.active_window()
                window.destroy_output_panel(panel_name)
                del panel_state[panel_name]

        debug('panel_state after for loop', panel_state)


class SideUpdateIndexPanelListener(sublime_plugin.ViewEventListener):
    def on_pre_close(self):
        file_name = self.view.file_name()
        if not file_name:
            return

        debug('UpdateIndexPanelListener for [ {} ]'.format(file_name))
        window = sublime.active_window()
        panel = window.find_output_panel(file_name)
        if panel:
            content = self.view.substr(Region(0, self.view.size()))
            debug('UpdateIndexPanelListener [ {} ], content: \n{}'.format(file_name, content))
            self.view.run_command('side_index_file', {
                'content': content,
                'panel_name': file_name
            })
            return

        debug('no index panel listener found for [ {} ]'.format(file_name))


class SideIndexFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, content, panel_name):
        debug('SideIndexFileCommand called')
        window = sublime.active_window()
        panel = window.find_output_panel(panel_name) or window.create_output_panel(panel_name)
        syntax = self.view.settings().get('syntax')
        panel.assign_syntax(syntax)
        debug('panel [ {} ] updated'.format(panel_name))
        panel.insert(edit, 0, content)

