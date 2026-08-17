class CodeEditor {

	static DEFAULTS = {
		theme: 'gruvbox-dark',
		mode: 'text/x-sql',
		lineNumbers: true,
		indentUnit: 4,
		tabSize: 4,
		lineWrapping: true,
	}

	constructor(element, options = {}) {
		this.options = { ...CodeEditor.DEFAULTS, ...options };
		this.editor = CodeMirror.fromTextArea(element, this.options);
	}

	getValue() {
		return this.editor.getValue();
	}

	setValue(text) {
		this.editor.setValue(text);
	}

	focus() {
		this.editor.focus();
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const textarea = document.querySelector('#sql-editor');
	if (textarea) {
		window.sqlEditor = new CodeEditor(textarea);
		window.sqlEditor.focus();
	}
});
