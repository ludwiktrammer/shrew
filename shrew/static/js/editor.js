import CodeMirror from "codemirror-minified";
import "codemirror-minified/mode/python/python";
import "codemirror-minified/addon/edit/closebrackets";


const textarea = document.getElementById("editor-code");

if (textarea) {
    let editor = CodeMirror.fromTextArea(textarea, {
        lineNumbers: true,
        theme: "shrew",
        indentUnit: 4,
        autofocus: true,
        autoCloseBrackets: true,
    });


    const buttonRun = document.getElementById("editor-run");
    const iframe = document.getElementById("interpreter-sandbox");
    const output = document.getElementById("code-output");
    const sandbox = iframe.contentWindow;

    buttonRun.addEventListener("click", () => {
        output.innerHTML = ''; // clear output
        sandbox.postMessage({code: editor.getValue()}, "*");
    });

    window.addEventListener("message", (event) => {
        if (event.data.shrewInterpreterReady === true) {
            buttonRun.disabled = false;
        }

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
