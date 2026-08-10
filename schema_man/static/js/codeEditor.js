class CodeEditor {

	static KEYWORDS = [
		'CREATE', 'TABLE', 'SELECT', 'FROM', 'INDEX',
		'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
		'DELETE', 'JOIN', 'ON', 'AND', 'OR', 'NOT',
		'NULL', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
		'ALTER', 'DROP', 'ADD', 'COLUMN', 'SET',
		'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT',
		'AS', 'DISTINCT', 'IN', 'BETWEEN', 'LIKE',
		'IS', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
		'CREATE', 'VIEW', 'TRIGGER', 'PROCEDURE', 'FUNCTION',
		'RETURN', 'RETURNS', 'BEGIN', 'COMMIT', 'ROLLBACK',
		'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE',
	]

	static OPERATORS = [
		'>=', '<=', '!=', '<>',
		'+', '-', '*', '/', '=',
		'<', '>', '%', '||',
	]

	constructor(textArea) {
		this.textArea = textArea;
	}

	syntaxHighlight() {

	}

	setLineNumbers() {

	}
}

