const divTerminal = document.getElementById("report-terminal");

function addAlerts(tables) {
	if (!divTerminal) {
		console.error("Report terminal is missing from the page");
		return;
	}

	if (!Array.isArray(tables)) {
		console.error("Report tables are missing from the response");
		return;
	}

	divTerminal.replaceChildren();

	for (const table of tables) {
		divTerminal.append(buildTable(table));
	}
}

function buildTable(table) {
	const block = document.createElement("div");
	block.className = "report-table";

	const header = document.createElement("div");
	header.className = "report-table-header";

	const name = document.createElement("span");
	name.className = "table-name";
	name.textContent = `Table: ${table.name}`;

	const level = document.createElement("span");
	level.className = "table-level";
	level.textContent = `Evaluated level: ${table.evaluated_level}`;

	const status = document.createElement("span");
	status.className = `status-label status-${table.status}`;
	status.textContent = table.status === "fails" ? "[ FAILS ]" : "[ PASSES ]";

	header.append(name, level, status);
	block.append(header);

	for (const alert of table.alerts) {
		const line = document.createElement("div");
		line.className = `alert alert-${alert.color.toLowerCase()}`;
		line.textContent = alert.message;
		block.append(line);
	}

	return block;
}
