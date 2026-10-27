import { basicSetup } from "codemirror";
import { EditorView } from "@codemirror/view";
import {sql} from "@codemirror/lang-sql";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";

const STORAGE_KEY = "schema.sql";
const container = document.querySelector("#sql-editor");

if (container) {
  const savedSql = sessionStorage.getItem(STORAGE_KEY);
  // Here window create sqlEditor, the instance of Code Mirror now is global
  window.sqlEditor = new EditorView({
    doc: savedSql ?? "-- PASTE, CREATE OR LOAD YOUR SQL SCHEMA",
    parent: container,
    extensions: [
      basicSetup,
      sql(),
      vscodeDark,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          sessionStorage.setItem(STORAGE_KEY, update.state.doc.toString());
        }
      }),
    ],
  });
}
