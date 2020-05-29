import Sk from "@microduino/skulpt";

import { drawFromActions } from "./drawing.js"

// Indicates whether there've been at least one successful run
let sucesfullRun = false;
let previewMode = document.location.search.replace("?","").split("&").includes("preview");
console.log(previewMode);

Sk.configure({
    output: output,
    uncaughtException: output,
    read: builtinRead,
    python3: true,
    execLimit: previewMode ? 30000 : 2000,
});
window.addEventListener("message", runCode);

// wait till everything loads
window.addEventListener("load", () => {
    window.parent.postMessage({type: "interpreter-ready"}, "*");
});

// run again when the tab is opened - sometimes background tab are slowed down by the browser
// and the execution of the code times out
document.addEventListener("visibilitychange", () => {
    if (!document.hidden && !sucesfullRun) {
        window.parent.postMessage({type: "interpreter-ready"}, "*");
    }
});

let outLines = [];
function output(message) {
    outLines.push(message);
}

function runCode(event) {
    if (event.origin !== location.origin) {
        // If the message came from a different domain
        // ignore it for security reasons.
        return;
    }
    if(!('code' in event.data)) {
        // Some other stray message, not our message
        // with code
        return;
    }
    outLines = []; // clear previous output

    // Add the implicit import of shrew functions
    let code = `from shrew import *\n\n${event.data.code}`;

    Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody("shrew-editor", false, code, true);
    }).then((result) => {
        let actions = skulptArrayToNativeArray(result.$d._shrew_actions__);
        drawFromActions(actions, (svg, hasAnimation) => {
            window.parent.postMessage({
                type: "run-result",
                out: outLines,
                svg: svg,
                hasAnimation: hasAnimation,
                code: event.data.code,
            }, "*");
        });
        sucesfullRun = true;
    }).catch((error) => {
        console.error(error);
        if (error.args) {
            window.parent.postMessage({
                type: "run-result",
                out: outLines,
                error: {
                    message: `${error.tp$name}: ${error.args.v[0].v}`,
                    lineNumber: error.traceback[error.traceback.length - 1].lineno - 2,
                }
            }, "*");
        } else {
            throw error;
        }
    })
}

function builtinRead(x) {
    if (window.skulptModules !== undefined && window.skulptModules[x] !== undefined) {
        return window.skulptModules[x];
    } else if (Sk.builtinFiles !== undefined && Sk.builtinFiles["files"][x] !== undefined) {
        return Sk.builtinFiles["files"][x];
    }
    throw "File not found: '" + x + "'";
}

/**
 * Recursively change skulpt-style array from Python into a standard array.
 */
function skulptArrayToNativeArray(a) {
    let result = [];
    if (a && a.v !== undefined) {
        a = a.v;
    }
    for (let element of a) {
        if (!element || element.v === undefined) {
            result.push(element)
        } else {
            let elementNative = element.v;
            if (Array.isArray(elementNative)) {
                result.push(skulptArrayToNativeArray(elementNative));
            } else {
                result.push(elementNative);
            }
        }
    }
    return result;
}
