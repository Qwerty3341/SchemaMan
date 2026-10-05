const runBtn = document.querySelector("#run-btn");

async function postSqlSchema() {
  const payload = {
    sql: window.sqlEditor.state.doc.toString(),
    dialect: document.querySelector(".select-for-sql").value,
    normalization_level: document.querySelector(".select-for-sql").value
  };

  try {
    const response = await fetch("/api/parse-sql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok) {
      alert(result.error);
      return;
    }
    alert("Valid SQL");
  } catch (error) {
    console.error("Error on send the SQL: ", error);
    alert(`Server error ${error}`);
  }
}

if (runBtn) {
  runBtn.addEventListener("click", postSqlSchema)
}

