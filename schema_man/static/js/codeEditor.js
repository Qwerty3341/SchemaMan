import { basicSetup } from "codemirror";
import { EditorView } from "@codemirror/view";
import {sql} from "@codemirror/lang-sql";
import { gruvboxDark } from "@uiw/codemirror-theme-gruvbox-dark";

const STORAGE_KEY = "schema.sql";
const container = document.querySelector("#sql-editor");

if (container) {
  const savedSql = sessionStorage.getItem(STORAGE_KEY);

  window.sqlEditor = new EditorView({
    doc: savedSql ?? "-- PASTE, CREATE OR LOAD YOUR SQL SCHEMA",
    parent: container,
    extensions: [
      basicSetup,
      sql(),
      gruvboxDark,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          sessionStorage.setItem(STORAGE_KEY, update.state.doc.toString());
        }
      }),
    ],
  });
}
