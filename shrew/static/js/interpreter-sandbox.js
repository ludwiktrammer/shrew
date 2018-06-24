import Sk from "skulpt";

Sk.configure({
    output: output,
    uncaughtException: output,
    read: builtinRead,
    python3: true,
});
window.addEventListener("message", runCode);


function output(x) {
    console.log(`ouput: ${x}`);
}

function runCode(event) {
    if (event.origin !== location.origin) {
        // If the message came from a different domain
        // ignore it for security reasons.
        return;
    }

    // ensure the string is never empty (to prevent Sk.importMainWithBody from switching its behavior
    // to importing a module named
    let code = event.data.code || " ";

    Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody("shrew-editor", false, code, true);
    }).then((result) => {
        console.log(result);
    }).catch((error) => {
        console.error(`${error.tp$name}: ${error.args.v[0].v}`);
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
