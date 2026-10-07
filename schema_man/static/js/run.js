const runBtn = document.querySelector("#run-btn");

async function postSqlSchema() {
  const sqlEditor = window.sqlEditor;
  const engineSelector = document.querySelector("#sql-engine-selector");
  const normalizationSelector = document.querySelector("#sql-normalization-selector");

  if (!sqlEditor || !engineSelector || !normalizationSelector) {
    console.error("Editor or SQL selectors are missing from the page");
    return;
  }

  const payload = {
    sql: sqlEditor.state.doc.toString(),
    dialect: engineSelector.value,
    normalization_level: normalizationSelector.value,
  };

  try {
    const response = await fetch("/api/parse-sql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok) {
      alert(result.error);
      return;
    }
    alert("SQL válido");
  } catch (error) {
    console.error("Error al enviar el SQL:", error);
    alert(`Error del servidor: ${error}`);
  }
}

if (runBtn) {
  runBtn.addEventListener("click", postSqlSchema);
}
