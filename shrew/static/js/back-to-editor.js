if (window.opener) {
    window.close();
    window.opener.postMessage({
        type: "logged-in",
    }, "*");
}
