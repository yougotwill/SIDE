import sublime
import sublime_plugin
import os
import linecache
import re


from SIDE.features.lib.helpers import defintion, get_word


history = []


class SideInfoPopup(sublime_plugin.TextCommand):
    def run(self, edit, location, point, is_class):
        file_path, relative_file_path, row_col = location 
        row, _col = row_col  # signiture row

        get_docs_params = {
            'file_path': file_path, 
            'row_above_signiture': row - 1,
            'row_below_signiture': None
        } 
        signiture = linecache.getline(file_path, row).strip()

        if is_class:
            signiture, row = self._build_up_class_signiture(signiture, 
                                                            file_path, 
                                                            row)
        else:
            signiture, row = self._build_up_function_signiture(signiture, 
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

        self.show_popup(content, point)
        linecache.clearcache()

    def show_popup(self, content, point):
        self.view.show_popup(content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, location=point, max_width=700)

    def _build_up_class_signiture(self, signiture, file_path, row):
        while '{' not in signiture and ':' not in signiture:
            row += 1
            signiture += ' ' + linecache.getline(file_path, row).strip()
        return signiture, row

    def _build_up_function_signiture(self, signiture, file_path, row):
        while ')' not in signiture:
            row += 1
            signiture += ' ' + linecache.getline(file_path, row).strip()
        return signiture, row

    def _get_docs(self, find_comment_params):
        file_path = find_comment_params['file_path']

        # extract docs above function
        row = find_comment_params['row_above_signiture']
        docs = linecache.getline(file_path, find_comment_params['row_above_signiture']).strip()
        # go in reverse
        if '*/' in docs:
            while '/*' not in docs:
                row -= 1
                docs = linecache.getline(file_path, row).strip() + '<br>' + docs
            return docs

        # extract docs below function
        row = find_comment_params['row_below_signiture']
        docs = linecache.getline(file_path, row).strip()
        if re.match('(\'\'\'|""")', docs):
            while not re.match('(\'\'\'|""").*?(\'\'\'|""")', docs,  re.MULTILINE):
                row += 1
                docs += '<br>' + linecache.getline(file_path, row).strip()
            return docs
        return ''
