import Sk from "skulpt";

import { drawFromActions } from "./drawing.js"

Sk.configure({
    output: output,
    uncaughtException: output,
    read: builtinRead,
    python3: true,
});
window.addEventListener("message", runCode);


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
        let actions = actionsSkulptToJs(result.$d._shrew_actions__);
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


function actionsSkulptToJs(actions) {
    console.log(actions);
    let result = [];
    for (let row of actions.v) {
        let [shapeID, command, value] = row.v;
        if (Array.isArray(value.v)) {
            value.v = value.v.map(e => e.v);
        }
        result.push([shapeID.v, command.v, value.v])
    }
    return result;
}
