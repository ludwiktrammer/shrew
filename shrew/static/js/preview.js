const $code = document.getElementById("preview-code");

if ($code) {
    const $iframe = document.getElementById("interpreter-sandbox");
    const sandbox = $iframe.contentWindow;

    window.addEventListener("message", (event) => {
        if (event.data.type === "interpreter-ready") {
            runCode();
        }
    });

    function runCode() {
        sandbox.postMessage({code: $code.textContent}, "*");
    }
}

