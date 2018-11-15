import sublime
import sublime_plugin
import os
import re
import linecache

from SIDE.features.lib.helpers import definition, get_word, get_function_name, get_line


class SideShowSignature(sublime_plugin.TextCommand):
    def run(self, edit, locations=None, point=None):
        if point is None:
            point = self.view.sel()[0].begin()

        word = None
        if locations is None:
            word = get_function_name(self.view, point)
            locations = definition(word, self.view)

        if len(locations) == 0:
            return

        # display the reference count
        if len(locations) > 1:
            content = """
            <body id="side-hover" style="margin:0">
                <div style="color: color(var(--foreground) alpha(0.7)); padding: 7px;">
                    {} definitions
                </div>
            </body>""".format(len(locations))
            self.view.show_popup(content, location=point)
            return

        file_path, relative_file_path, row_col = locations[0]
        row, _col = row_col  # signiture row

        get_docs_params = {
            'file_path': file_path, 
            'row_above_signiture': row - 1,
            'row_below_signiture': None
        }

        function_line = get_line(self.view, file_path, row).strip()

        signiture, row = self.get_signiture(function_line, 
                                            file_path, 
                                            row)
        # prettify signiture
        signiture = signiture.strip('{').strip(':')

        get_docs_params['row_below_signiture'] = row + 1 
        docs = self._get_docs(get_docs_params)  
        if docs:
            docs = """
            <div style="padding: 7px; 
                        border-top: 1px solid color(var(--foreground) alpha(0.1))">
                {}
            </div>""".format(docs)

        # prettyfy file origin
        if len(relative_file_path) > 70:
            relative_file_path = '...' + relative_file_path[-50:]
        
        origin = """
        <div style="padding: 7px; 
                    border-top: 1px solid color(var(--foreground) alpha(0.1));
                    color: color(var(--foreground) alpha(0.7))">
            {}
        </div>""".format(relative_file_path)

        content = """
        <body id="side-hover" style="margin:0">
            <div style="color: var(--orangish); 
                        padding: 7px;">
                {}
            </div>
            {} 
            {}
        </body>""".format(signiture, origin, docs)

        self._show_popup(content, point)
        # end of command execution
        # perfect place to clear the linecache
        linecache.clearcache()

    def _show_popup(self, content, point):
        self.view.show_popup(content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, location=point, max_width=700)

    def get_signiture(self, signiture, file_path, row):
        while '{' not in signiture and ':' not in signiture and ')' not in signiture :
            row += 1
            signiture += ' ' + get_line(self.view, file_path, row).strip()
        return signiture, row

    def _get_docs(self, find_comment_params):
        file_path = find_comment_params['file_path']

        # extract docs above function
        row = find_comment_params['row_above_signiture']
        docs = get_line(self.view, file_path, row).strip()
        # go in reverse
        if '*/' in docs:
            while '/*' not in docs:
                row -= 1
                docs = get_line(self.view, file_path, row).strip() + '<br>' + docs
            return docs

        # extract docs below function
        row = find_comment_params['row_below_signiture']
        docs = get_line(self.view, file_path, row).strip()
        if re.match('(\'\'\'|""")', docs):
            while not re.match('(\'\'\'|""").*?(\'\'\'|""")', docs,  re.MULTILINE):
                row += 1
                docs += '<br>' + get_line(self.view, file_path, row).strip()
            return docs
        return ''
