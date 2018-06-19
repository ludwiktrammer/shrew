(function($B){
    $B.brython({ipy_id: []});

    // Remove modules for interacting with the browser
    delete $B.imported["browser"];
    delete $B.imported["browser.html"];
    delete $B.imported["javascript"];

    let code = document.getElementById("editor-code");
    let button = document.getElementById("editor-run");
    button.addEventListener("click", () => {
        // $B.$py_module_path['__main__'] = $B.brython_path;
        try {
            let js = $B.py2js(code.value, "__main__", "__main__", $B.builtins_scope).to_js();
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
});
})(__BRYTHON__);
