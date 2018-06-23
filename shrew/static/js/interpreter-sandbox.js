(function($B){
    // Initiate Brython
    $B.brython({
        ipy_id: [],
        static_stdlib_import: false,
        pythonpath: ["/static/python"],
    });

    // Remove modules for interacting with the browser
    delete $B.imported["browser"];
    delete $B.imported["browser.html"];
    delete $B.imported["javascript"];

    window.addEventListener("message", runCode);

    function runCode(event) {
        if (event.origin !== location.origin) {
            // If the message came from a different domain
            // ignore it for security reasons.
            return;
        }

        // Add implicit imports
        let pythonCode = "from drawing import *\n\n" + event.data.code;

        // $B.$py_module_path['__main__'] = $B.brython_path;
        try {
            let js = $B.py2js(pythonCode, "__main__", "__main__", $B.builtins_scope).to_js();
            eval(js);
        } catch($err) {
            // If the error was not caught by the Python runtime, build an
            // instance of a Python exception
            if($err.$py_error === undefined){
                console.log('Javascript error', $err);
                $err = $B.builtins.RuntimeError.$factory($err + '')
            }

            let $trace = $B.builtins.getattr($err,'info') + '\n' + $err.__class__.__name__ +
                ': ' + $err.args;
            console.log($trace);
        }
    }
})(__BRYTHON__);
