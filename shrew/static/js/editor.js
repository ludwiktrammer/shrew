const editor = document.getElementById("editor-code");

if (editor) {
    const buttonRun = document.getElementById("editor-run");
    const iframe = document.getElementById("interpreter-sandbox");
    const output = document.getElementById("code-output");
    const sandbox = iframe.contentWindow;

    buttonRun.addEventListener("click", () => {
        output.innerHTML = ''; // clear output
        sandbox.postMessage({code: editor.value}, "*");
    });

    window.addEventListener("message", (event) => {
        if (event.data.message !== undefined) {
            let pre = document.createElement('pre');
            pre.innerText = event.data.message;
            if (event.data.error) {
                pre.classList.add("error");
            }
            output.appendChild(pre);
            console.log(event.data.message);
        }
    });

}
