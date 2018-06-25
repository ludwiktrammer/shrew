import Sk from "skulpt";
import { drawFromActions } from "./drawing.js"

Sk.configure({
    output: output,
    uncaughtException: output,
    read: builtinRead,
    python3: true,
});
window.addEventListener("message", runCode);
window.parent.postMessage({shrewInterpreterReady: true}, "*");


function output(message, error) {
    error = error || false;
    window.parent.postMessage({message: message, error: error}, "*");
}

function runCode(event) {
    if (event.origin !== location.origin) {
        // If the message came from a different domain
        // ignore it for security reasons.
        return;
    }

    // Add the implicit import of shrew functions
    let code = `from shrew import *\n\n${event.data.code}`;

    Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody("shrew-editor", false, code, true);
    }).then((result) => {
        let actions = skulptArrayToNativeArray(result.$d._shrew_actions__);
        drawFromActions(actions);
    }).catch((error) => {
        if (error.args) {
            console.log(error);
            output(`${error.tp$name}: ${error.args.v[0].v} (line ${error.traceback[error.traceback.length - 1].lineno - 2})`, true);
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
