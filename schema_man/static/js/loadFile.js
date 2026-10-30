// ======================
// Load the SQL in editor 
// ======================

const fileInput = document.getElementById("file-chooser");
const fileNameSpan = document.getElementById("file-name-span");

document.getElementById("load-sql-label").addEventListener('click', () => {
	fileInput.click();
});

fileInput.addEventListener('change', async () => {
	const file = fileInput.files[0];
	if (!file) return;

	fileNameSpan.textContent = file.name;
	const editor = window.sqlEditor;

	if (!editor) {
		console.error("CodeMirror editor not available");
		return;
	}

	try {
		const sqlCode = await file.text();
		editor.dispatch({
			changes: {
				from: 0,
				to: editor.state.doc.length,
				insert: sqlCode
			}
		})
	} catch (e) {
		console.error("Could not read selected file", e)
	}
});
