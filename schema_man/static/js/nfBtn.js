const previousBtn = document.getElementById("previous-btn");
const nextBtn = document.getElementById("next-btn");

const flow = ["/nf/nf1", "/nf/nf2", "/nf/nf3", "/nf/bcnf", "/nf/nf4", "/nf/nf5"];

function setLink(btn, href) {
	if (href) {
		btn.href = href;
		btn.classList.remove("disabled");
	} else {
		btn.removeAttribute("href");
		btn.classList.add("disabled");
	}
}

function changeHref() {
	const pathname = window.location.pathname.replace(/\/$/, "");
	const index = flow.indexOf(pathname);

	// Not a normal forms (nf) page
	if (index === -1) return;
	setLink(previousBtn, flow[index - 1]);
	setLink(nextBtn, flow[index + 1]);
}

changeHref();
