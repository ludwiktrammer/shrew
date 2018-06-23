import Sk from "skulpt";

Sk.configure({
    output: output,
    read: builtinRead,
    python3: true,
});
window.addEventListener("message", runCode);


function output(x) {
    console.log(x);
}

function runCode(event) {
    if (event.origin !== location.origin) {
        // If the message came from a different domain
        // ignore it for security reasons.
        return;
    }

    Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody("<stdin>", false, event.data.code, true);
    });
}

function builtinRead(x) {
    if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
        throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}
