document.addEventListener('DOMContentLoaded', () => {
	const runButton = document.querySelector('#reporter-run');
	const engineSelector = document.querySelector('#sql-engine-selector');

	// Elements on the dialog
	const dialog = document.getElementById("validation-dialog");
	const h2Dialog = document.getElementById("vd-error");
	const messageP = document.getElementById("vd-error-message");
	const btnCloseDialog = document.getElementById("vd-btn-close");

	if (!runButton || !engineSelector || !dialog || !h2Dialog || !messageP || !btnCloseDialog || !window.sqlEditor) {
		return;
	}

	// Dialog logic
	const showDialog = (title, message, type) => {
		h2Dialog.textContent = title;
		messageP.textContent = message;
		dialog.className = type;

		if (!dialog.open) {
			dialog.showModal();
		}
	};

	btnCloseDialog.addEventListener('click', () => {
		dialog.close();
	});

	runButton.addEventListener('click', async () => {
		showDialog("Sending the schema to sqlglot", "Validating the schema", 'status')

		try {
			const response = await fetch('/api/validate', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					sql: window.sqlEditor.getValue(),
					dialect: engineSelector.value,
				}),
			});

			const result = await response.json();

			if (!response.ok) {
				throw new Error(result.errors?.join('\n') || 'Validation Error');
			}
			
			if (result.valid === true) {
				showDialog("Correct", "SQL without errors", "success");
			} else { // Error in the schema
				showDialog(
					"Incorrect",
					result.errors?.join('\n') || "SQL with errors",
					"error"
				);
			}

		} catch (error) {
			showDialog("Error", error.message || "Could not validate the schema", 'error')
		}
	});
});
