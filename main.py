from SIDE.features.definition import SideJumpBack, SideDefinition
import os
import sublime
import sublime_plugin
import linecache
import re


class SideHover(sublime_plugin.ViewEventListener):
    def on_hover(self, point, hover_zone):
        scope_name = self.view.scope_name(point)
        if hover_zone != sublime.HOVER_TEXT:
            return

        if 'function' in scope_name:
            self.handle_hover(point)

        if 'class' in scope_name or 'constructor' in scope_name:
            self.handle_hover(point, True)
        

    def handle_hover(self, point, is_class=False):
        word = get_word(self.view, point)
        locations = defintion_in_open_files(word) or defintion(word)

        filename, file_extension = os.path.splitext(self.view.file_name())
        locations = locations_by_file_extension(locations, file_extension)

        definition_count = len(locations)

        if definition_count > 1:
            content = """
                <body id="side-hover" style="margin:0">
                    <div style="color: color(var(--foreground) alpha(0.7)); 
                                padding: 7px;">{} definitions</div>
                </body>""".format(definition_count)
            self.show_popup(content, point)


        content = ''
        if len(locations) == 1:
            location = locations[0]
            file_path, relative_file_path, row_col = location
            row = row_col[0]
            find_comment_params = {'file_path': file_path, 'above_function': row - 1} 

            signiture = linecache.getline(file_path, row).strip()
            if is_class:
                while '{' not in signiture and ':' not in signiture:
                    row += 1
                    signiture += ' ' + linecache.getline(file_path, row).strip()
            else:
                while ')' not in signiture:
                    row += 1
                    signiture += ' ' + linecache.getline(file_path, row).strip()
            find_comment_params['below_function'] = row + 1 
            signiture = signiture.strip('{').strip(':')

            docs = self.get_docs(find_comment_params)  
            if docs:
                docs = """
                    <div style="padding: 7px; 
                                border-top: 1px solid color(var(--foreground) alpha(0.1))">
                                {}
                    </div>""".format(docs)
            
            if len(relative_file_path) > 70:
                relative_file_path = '...' + relative_file_path[-50:]
            
            ref = """
                <div style="padding: 7px; 
                            border-top: 1px solid color(var(--foreground) alpha(0.1));
                            color: color(var(--foreground) alpha(0.7))">
                    {}
                </div>""".format(relative_file_path)

            content = """
            <body id="side-hover" style="margin:0">
                <div style="color: var(--orangish); 
                            padding: 7px;">{}</div>
                {} {}
            </body>""".format(signiture, ref, docs)
            self.show_popup(content, point)
            linecache.clearcache()

    def show_popup(self, content, point):
        self.view.show_popup(content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, location=point, max_width=700)
    
    def get_docs(self, find_comment_params):
        file_path = find_comment_params['file_path']
        row = find_comment_params['above_function']
        docs = linecache.getline(file_path, find_comment_params['above_function']).strip()
        if '*/' in docs:
            while '/*' not in docs:
                row -= 1
                docs = linecache.getline(file_path, row).strip() + '<br>' + docs
            return docs

        row = find_comment_params['below_function']
        docs = linecache.getline(file_path, row).strip()
        if '"""' in docs:
            while not re.match('""".*?"""', docs,  re.MULTILINE):
                row += 1
                docs += '<br>' + linecache.getline(file_path, row).strip()
            return docs
        if "'''" in docs:
            while not re.match("'''.*?'''", docs,  re.MULTILINE):
                row += 1
                docs += '<br>' + linecache.getline(file_path, row).strip()
            return docs

        return ''
