import sublime
import sublime_plugin
import linecache

from SIDE.features.lib.helpers import get_word, reference, get_project_path, get_line

last_reference_word = ''

class SideReference(sublime_plugin.TextCommand):
    def run(self, edit):
        global last_reference_word
        window = sublime.active_window()
        word = get_word(self.view)

        is_same_word = last_reference_word == word
        panel = window.find_output_panel("references")
        print('panel')
        if panel is not None and is_same_word:
            window.destroy_output_panel('references')
            return


        locations = reference(word, self.view)

        if len(locations) == 0:
            sublime.status_message('No references')

        last_reference_word = word
        find_result = ''
        for location in locations:
            file_path, rel_file_path, row_col = location
            row, col = row_col
            line = get_line(self.view, file_path, row).strip()
            
            find_result += "{}:\n    {}:{}        {}\n".format(rel_file_path, row, col, line)

        panel = window.create_output_panel("references")
        base_dir = get_project_path(window)

        panel.settings().set("gutter", False)
        panel.settings().set("result_base_dir", base_dir)
        panel.settings().set("result_file_regex", r"^(\S.*):$")
        panel.settings().set("result_line_regex", r"^\s+([0-9]+):([0-9]+).*$")
        panel.assign_syntax('Packages/Default/Find Results.hidden-tmLanguage')
        panel = window.create_output_panel("references")

        window.run_command("show_panel", {"panel": "output.references"})

        
        panel.run_command('append', {
            'characters': " {} references for '{}'\n\n{}".format(len(locations), word, find_result),
            'force': True,
            'scroll_to_end': False
        })

        regions = panel.find_all(r"\b{}\b".format(word))
        panel.add_regions('highlight_references', regions, 'comment', flags=sublime.DRAW_OUTLINED)
       
        panel.set_read_only(True)
        # perfect place to clear the linecache
        linecache.clearcache()




