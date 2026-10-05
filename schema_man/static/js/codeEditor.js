import { basicSetup } from "codemirror";
import { EditorView } from "@codemirror/view";
import {sql} from "@codemirror/lang-sql";
import { gruvboxDark } from "@uiw/codemirror-theme-gruvbox-dark";

const container = document.querySelector("#sql-editor");

window.sqlEditor = new EditorView({
	doc: "-- PASTE, CREATE OR LOAD YOUR SQL SCHEMA",
	parent: container,
	extensions: [
		basicSetup,
		sql(),
		gruvboxDark
	]
})
