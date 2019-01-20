## SIDE 

SIDE makes Sublime just a bit more useful.
The goal of SIDE is to mimic LSP features without language servers and without any protocol. It uses only the things that are already in Sublime.

How is that even possible?
Well SIDE is smart as much as you are. 
You can be the best or the worst language server. That depends on you. 
SIDE will just try to help as much as it can.

### Features
* Definition
* Hover
* Show Signature
* Completion
* Reference
* Code Lens
* Code Actions
* Rename
* Highlight
* Diagnostic

**Show signature help** when hovering over `function/class` symbols. 
Or when typing a `(` after a function call.
Or a `,` when typing the function arguments. 

You can also assign a key binding to trigger it manually.

![signature help](img/signature.png)

**Highlight** will underline the word under cursor, smartly. 

Green underline means that SIDE will highlight only the word in the given function scope. 
Unless the word is a function. In that case it will highlight all the word occurrences in the file.

Yellow underline means that SIDE can't figure out the scope.
In which case it will highlight all occurrences of the word in the file.

**Highlight** and **Rename** work hand in hand.

Rename will select all the highlighted words for editing.

![rename](img/rename.png)

Rename can also select all occurrences of the word in a file. 

![rename all](img/rename_all.png)

**Reference** panel shows all references for the given symbol. 
Sometimes it is useful to cycle through the references in just the open views, in which case you can assign a key binding.   

![References](img/references.png)

**Completions** will show all the symbols and words found in the opened views, with the type of the symbol and the file from where it is found. The types can be:
* `[c]` - class
* `[m]` - method
* `[f]` - function
* `[s]` - struct
* `[#]` - unknown, but it exist somewhere in the open views, probably a variable, or a word in a comment

SIDE has a feature called **One Level Indexing**. Here is how it works.
If SIDE is 100% sure that some file `B` is related to the current file `A` you are editing.
It will show you all the symbols defined it that file `B` in completions. 

![Completions](img/completions.png)

Code lens show you the count of references and definitions.

![Code lens](img/codelens.png)

Never misspell a function name again. Just set Sublime's `spell_check` setting to `true`. 

![Code actions](img/codeactions.png)

Code actions can correct spelling mistakes and search the Internet.

When you need an advice or a Yes/No answer, ask SIDE and it will give one. 

SIDE <3 Chuck Norris. Chuck will help you to get through the day with a smile. :)

### Configure SIDE

Assign key bindings you would want to use by opening `Preferences/Package Settings/SIDE/Key Bindings` menu.

Sometimes you need to configure SIDE to know what are references or definitions, because the default `SOME_LANGAUGE.tmPreferences` didn't account for them. 
Or there are symbols you would like to remove from the index. 

Here is how to configure your language `X` for SIDE and Sublime. 

#### Adding references

Create a `{YourLanguage}References.tmPreferences`. 
Save it to your `Packages\User` or `SIDE/languages` (if you plan to do a Pull Request, PR are welcome) folder, with the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
	<key>scope</key>
	<string>{a list of scopes}</string> // <-- add your scopes here
	<key>settings</key>
	<dict>
		<key>showInIndexedReferenceList</key>
		<string>1</string>
	</dict>
</dict>
</plist>
```
> All the strings bellow `scope` key will be added to the references list. 

Here is how SIDE's configuration for rust references looks like. The file is named `RustReferences.tmPreferences` and is placed in `SIDE/languages` folder.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
	<key>scope</key>
	<string>support.function.rust</string>
	<key>settings</key>
	<dict>
		<key>showInIndexedReferenceList</key>
		<string>1</string>
	</dict>
</dict>
</plist>
```

#### Adding definitions 

Create a `{YourLanguage}IndexedSymbols.tmPreferences`. Save it to your `Packages\User` or `SIDE/languages`(if you plan to do a Pull Request) folder.

Here is how SIDE's configuration for rust definitions looks like.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
	<key>name</key>
	<string>Rust Symbols</string>
	<key>scope</key>
	<string>entity.name.function.rust, entity.name.macro.rust, entity.name.struct.rust, entity.name.enum.rust, entity.name.module.rust, entity.name.type.rust, entity.name.impl.rust, entity.name.trait.rust</string>
	<key>settings</key>
	<dict>
		<key>showInIndexedSymbolList</key>
		<integer>1</integer>
	</dict>
</dict>
</plist>
```

### What is the point of SIDE?

The point of SIDE is to make you think. It is great to have great auto completion, diagnostics, ..., but where is the fun in that.

When you use SIDE, it won't warn you if you make mistakes (except if it is a spelling mistake and you enabled spell checking). We all make mistakes and we should learn from them.
