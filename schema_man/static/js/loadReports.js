const divTerminal = document.getElementById("report-terminal");

function addAlerts(report) {
	if (!divTerminal) {
		console.error("Report terminal is missing from the page");
		return;
	}

	divTerminal.textContent = report;
}
