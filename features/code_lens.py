import sublime
import sublime_plugin

from SIDE.features.lib.helpers import reference, get_word, defintion, is_function, is_class

phantom_sets_by_buffer = {}  # type: Dict[buffer_id, PhantomSet]


class SideCodeLens(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        global phantom_sets_by_buffer

        buffer_id = self.view.buffer_id()
        phantom_set = phantom_sets_by_buffer.get(buffer_id)
        if not phantom_set:
            phantom_set = sublime.PhantomSet(self.view, 'references_phantom')
            phantom_sets_by_buffer[buffer_id] = phantom_set
    
        point = self.view.sel()[0].begin()
        word_region = self.view.word(point)

        word = self.view.substr(word_region)
        scope_name = self.view.scope_name(word_region.begin())

        phantoms = []
        if is_function(scope_name) or is_class(scope_name):

            text = []
            if is_function(scope_name):
                reference_count = len(reference(word, self.view))
                if reference_count == 1:
                    text.append("{} reference".format(reference_count))
                else:
                    text.append("{} references".format(reference_count))

            defintion_count = len(defintion(word, self.view))
            if defintion_count == 1:
                text.append("{} definition".format(defintion_count))
            else:
                text.append("{} definitions".format(defintion_count))
           
            content = """
            <body id="side-references" style="color: color(var(--foreground) alpha(0.4))">
                <small style="margin:0;padding:0;">{}</small>
            </body>
            """.format(" | ".join(text))

            phantoms.append(sublime.Phantom(word_region, content, sublime.LAYOUT_BELOW))
            phantom_set.update(phantoms)
        else: 
            # outside of function word
            phantom_sets_by_buffer.pop(buffer_id, None)