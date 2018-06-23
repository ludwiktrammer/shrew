const editor = document.getElementById("editor-code");

if (editor) {
    const buttonRun = document.getElementById("editor-run");
    const iframe = document.getElementById("interpreter-sandbox");
    const sandbox = iframe.contentWindow;

    buttonRun.addEventListener("click", () => {
        sandbox.postMessage({code: editor.value}, "*");
    });
}
