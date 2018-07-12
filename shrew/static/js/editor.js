import CodeMirror from "codemirror-minified";
import "codemirror-minified/mode/python/python";
import "codemirror-minified/addon/edit/closebrackets";
import "codemirror-minified/addon/lint/lint";
import * as Cookies from "js-cookie";
import Timeago from 'timeago.js';

import replaceError from "./error-replacements.js";

const $editor = document.getElementById("shrew-editor");
if ($editor) {
    const $textarea = document.getElementById("editor-code");
    const $iframe = document.getElementById("interpreter-sandbox");
    const $output = document.getElementById("code-output");
    const $name = document.getElementById("name");
    const $saveButton = document.getElementById("saveButton");
    const $saveButtonCaption = document.querySelector("#saveButton .caption");
    const $saveButtonTime = document.querySelector("#saveButton .time");
    const sandbox = $iframe.contentWindow;
    let unsaved = $editor.classList.contains("unsaved");
    let slug = $textarea.dataset.slug;
    let name = $textarea.dataset.name;
    let timeago = Timeago();
    let isDirty = false; // did something changed
    let showErrorsTimeout;
    let lastPositiveResult;

    let editor = CodeMirror.fromTextArea($textarea, {
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

    editor.on("change", () => {
        isDirty = true;
    });

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
                updateCreation(event.data);
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

    $name.addEventListener("click", () => {
        if (lastPositiveResult !== undefined) {
            if (askForName()) {
                saveCreation();
            }
        }
    });

    $saveButton.addEventListener("click", () => {
        if (lastPositiveResult !== undefined) {
            let newName;
            if (unsaved) {
                newName = askForName();
            }
            if (!unsaved || newName) saveCreation();
        }
    });

    function askForName() {
        const adjectives = [
            "cool",
            "beautiful",
            "awesome",
            "wonderful",
        ];
        let type = lastPositiveResult.hasAnimation ? "animation" : "drawing";
        let adjective = adjectives[Math.floor(Math.random()*adjectives.length)];
        let newName = window.prompt(`What do you want to name this ${adjective} ${type}?`, name);
        if (newName) {
            name = newName;
        }
        return newName;
    }

    function updateCreation(executionResults) {
        lastPositiveResult = executionResults;
        $editor.classList.remove("no-output");
        if (unsaved) {  // don't send updates to the server if unsaved
            // Update the "Unsaved..." text to reflect the kind of creation
            let $kind = document.querySelector("#name .kind");
            if ($kind) {
                $kind.innerHTML = executionResults.hasAnimation ? "animation" : "drawing";
            }
        } else if (isDirty) {
            saveCreation();
        }
    }

    function saveCreation() {
        $saveButton.classList.add("is-loading");

        let data = {
            slug: slug,
            name: name,
            code: lastPositiveResult.code,
            svg: lastPositiveResult.svg,
            is_animated: lastPositiveResult.hasAnimation,
        };
        fetch('/creations/api-save', {
            credentials: 'include',
            method: 'POST',
            body: JSON.stringify(data),
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            }
        }).then(response => {
            if (response.status === 200) {
                response.json().then(creationProperties => {
                    if (creationProperties.slug) { // ensure proper format
                        $saveButton.classList.remove("is-loading");
                        slug = creationProperties.slug;
                        name = creationProperties.name;
                        unsaved = false;
                        $name.innerText = name;
                        $saveButtonCaption.innerText = "Saved";
                        $editor.classList.remove("unsaved");

                        Timeago.cancel();
                        timeago.doRender($saveButtonTime, new Date());

                        let title = `${name} - Code Shrew`;
                        history.replaceState(slug, title, creationProperties.url);
                        document.title = title;
                    }
                });
            }
        })
    }

    /**
     * Display results to the "console"
     */
    function displayResults(lines, error) {
        $output.innerHTML = ''; // clear output
        if (lines.length || error) {
            $output.classList.add("has-output");
        } else {
            $output.classList.remove("has-output");
        }

        for (let line of lines) {
            let pre = document.createElement('pre');
            pre.innerText = line;
            $output.appendChild(pre);
        }
        let errors = [];
        if (error) {
            let message = replaceError(error.message);
            let lineNumber = error.lineNumber;

            let pre = document.createElement('pre');
            pre.innerText = `${message} (line ${lineNumber})`;
            pre.classList.add("error");
            $output.appendChild(pre);

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

