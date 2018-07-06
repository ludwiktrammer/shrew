import CodeMirror from "codemirror-minified";
import "codemirror-minified/mode/python/python";
import "codemirror-minified/addon/edit/closebrackets";
import "codemirror-minified/addon/lint/lint";

import replaceError from "./error-replacements.js";

const textarea = document.getElementById("editor-code");

if (textarea) {
    const iframe = document.getElementById("interpreter-sandbox");
    const output = document.getElementById("code-output");
    const sandbox = iframe.contentWindow;
    let showErrorsTimeout;

    let editor = CodeMirror.fromTextArea(textarea, {
        lineNumbers: true,
        theme: "shrew",
        indentUnit: 4,
        autofocus: true,
        autoCloseBrackets: true,
        lint: {
            getAnnotations: runLint,
            async: true,
        },
        gutters: ["CodeMirror-lint-markers"],
    });
    let lintCallback;
    let shrewInterpreterReady = false;

    function runCode() {
        sandbox.postMessage({code: editor.getValue()}, "*");
    }

    function runLint(text, callback) {
        if (shrewInterpreterReady) {
            runCode();
        }
        lintCallback = callback;
    }

    window.addEventListener("message", (event) => {
        if (event.data.type === "interpreter-ready") {
            shrewInterpreterReady = true;
            runCode();
        } else if(event.data.type === "run-result") {
            clearTimeout(showErrorsTimeout);
            if(!event.data.error) {
                displayResults(event.data.out);
            } else {
                // errors during typing are annoying
                // wait additional 2 seconds - maybe the error will be fixed by then
                showErrorsTimeout = setTimeout(() => {
                    displayResults(event.data.out, event.data.error);
                }, 2000);
            }
        }
    });

    /**
     * Display results to the "console"
     */
    function displayResults(lines, error) {
        output.innerHTML = ''; // clear output
        if (lines.length || error) {
            output.classList.add("has-output");
        } else {
            output.classList.remove("has-output");
        }

        for (let line of lines) {
            let pre = document.createElement('pre');
            pre.innerText = line;
            output.appendChild(pre);
        }
        let errors = [];
        if (error) {
            let message = replaceError(error.message);
            let lineNumber = error.lineNumber;

            let pre = document.createElement('pre');
            pre.innerText = `${message} (line ${lineNumber})`;
            pre.classList.add("error");
            output.appendChild(pre);

            errors.push({
                from: CodeMirror.Pos(lineNumber - 1),
                to: CodeMirror.Pos(lineNumber - 1),
                message: message,
            });
        }
        if (lintCallback) {
            lintCallback(errors);
        }
    }
}

