import {EditorView, basicSetup} from "codemirror";
import {sql} from "@codemirror/lang-sql"

const editor = new EditorView({
	doc: "Paste your SQL code here"
	extensions: [

	]
});
