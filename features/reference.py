import sublime
import sublime_plugin
import linecache

from SIDE.features.lib.helpers import get_word, reference, get_project_path, get_line, open_view, chose_one_location_from_many


class SideReference(sublime_plugin.TextCommand):
    def run(self, edit, find_all=True):
        window = sublime.active_window()
        word = get_word(self.view)

        locations = reference(word, self.view, find_all)

        if len(locations) == 0:
            window.destroy_output_panel('references')
            self.view.show_popup('No References', sublime.HIDE_ON_MOUSE_MOVE_AWAY)
            return

        panel = window.find_output_panel("references")
        if len(locations) == 1:
            open_view(locations[0], self.view)
            if panel is not None:
                window.destroy_output_panel('references')
            return

        if len(locations) > 1:
            if not find_all:
                chose_one_location_from_many(locations, self.view)
                return 

            find_result = ''
            for location in locations:
                file_path, rel_file_path, row_col = location
                row, col = row_col
                line = get_line(self.view, file_path, row).strip()  
                find_result += "{}:\n\t{}:{}\t\t{}\n\n".format(rel_file_path, row, col, line)

            panel = window.create_output_panel("references")
            
            base_dir = get_project_path(window)
            panel.settings().set("result_base_dir", base_dir)

            panel.settings().set("gutter", False)
            panel.settings().set("result_file_regex", r"^(\S.*):$")
            panel.settings().set("result_line_regex", r"^\s+([0-9]+):([0-9]+).*$")
            panel.settings().set("draw_white_space", "none")
            panel.assign_syntax('Packages/Default/Find Results.hidden-tmLanguage')

            panel = window.create_output_panel("references")

            window.run_command("show_panel", {"panel": "output.references"})
            panel.run_command('append', {
                'characters': "{} references for '{}'\n\n{}".format(len(locations), word, find_result),
                'force': True,
                'scroll_to_end': False
            })
            panel.set_read_only(True)

            # highlight region
            regions = panel.find_all(r"\b{}\b".format(word))
            panel.add_regions('highlight_references', regions, 'comment', flags=sublime.DRAW_OUTLINED)
           
            # perfect place to clear the linecache
            linecache.clearcache()

