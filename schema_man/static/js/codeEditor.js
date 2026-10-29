import {basicSetup} from "codemirror";
import {EditorView} from "@codemirror/view";
import {sql} from "@codemirror/lang-sql";
import {vscodeDark} from "@uiw/codemirror-theme-vscode";

const STORAGE_KEY = "schema.sql";
const container = document.querySelector("#sql-editor");

//const customBackground = EditorView.theme(
  //{
    //"&": {backgroundColor: "#0B0B0B", color: "#F5E6D3"},
    //".cm-scroller": { backgroundColor: "#0B0B0B" },
    //".cm-gutters": { backgroundColor: "#0B0B0B", color: "#F5E6D3" },
  //},
  //{dark: true}
//);
//

if (container) {
  const savedSql = sessionStorage.getItem(STORAGE_KEY);
  // Here window create sqlEditor, the instance of Code Mirror now is global
  window.sqlEditor = new EditorView({
    doc: savedSql ?? "YOUR SCHEMA GOES HERE",
    parent: container,
    extensions: [
      basicSetup,
      sql(),
      vscodeDark,
      //customBackground,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          sessionStorage.setItem(STORAGE_KEY, update.state.doc.toString());
        }
      }),
    ],
  });
}
