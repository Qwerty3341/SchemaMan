document.addEventListener('DOMContentLoaded', () => {
	const textarea = document.querySelector('#sql-editor');
	const runButton = document.querySelector('#reporter-run');
	const engineSelector = document.querySelector('#sql-engine-selector');
	const reportPage = document.querySelector('.report-page');

	if (!textarea || !runButton || !engineSelector || !reportPage || !window.sqlEditor) {
		return;
	}

	runButton.addEventListener('click', async () => {
		reportPage.textContent = 'Validando...';

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
				throw new Error(result.errors?.join('\n') || 'Error de validación');
			}

			reportPage.textContent = result.valid
				? 'El SQL es válido.'
				: result.errors.join('\n');
		} catch (error) {
			reportPage.textContent = error.message;
		}
	});
});
