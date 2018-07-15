import * as Cookies from "js-cookie";
import Timeago from 'timeago.js';


const $code = document.getElementById("preview-code");

if ($code) {
    const $iframe = document.getElementById("interpreter-sandbox");
    const sandbox = $iframe.contentWindow;
    const $creationTime = document.getElementById("creation-time");

    let timeago = new Timeago();
    timeago.render($creationTime);

    window.addEventListener("message", (event) => {
        if (event.data.type === "interpreter-ready") {
            runCode();
        }
    });

    function runCode() {
        sandbox.postMessage({code: $code.textContent}, "*");
    }
}


const $love = document.getElementById("love");
const $loveLabel = document.querySelector("#love .love-label");
$love.addEventListener("click", () => {
    if ($love.dataset.isAuthenticated !== "1") {
        redirectToLogin();
        return;
    }
    if ($love.dataset.active === "1") {
        buttonUnlove();
        apiSendLove("unlove").catch(buttonLove);
    } else {
        buttonLove();
        apiSendLove("love").catch(buttonUnlove);
    }
});

function redirectToLogin() {
    document.location.href = `/accounts/login/?next=${document.location.pathname}`
}

/**
 * Set the button state to loving.
 */
function buttonLove() {
    $love.classList.remove("is-outlined");
    $love.dataset.badge++;
    $love.classList.add("badge");
    $love.dataset.active = 1;
    $loveLabel.textContent = "Unlove";
    $love.blur();
}

/**
 * Set the button state to not loving.
 */
function buttonUnlove() {
    $love.classList.add("is-outlined");
    $love.dataset.badge--;
    if ($love.dataset.badge <= 0) {
        $love.classList.remove("badge");
    }
    $love.dataset.active = 0;
    $loveLabel.textContent = "Love";
    $love.blur();
}

function apiSendLove(action) {
    return fetch('/show/__api-love', {
        credentials: 'include',
        method: 'POST',
        body: JSON.stringify({
            'slug': $love.dataset.slug,
            'author': $love.dataset.author,
            'action': action,
        }),
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': Cookies.get('csrftoken'),
        }
    }).then(response => {
        if (response.status === 403) {
            redirectToLogin();
        }
        if (response.status !== 200) {
            throw "Server responded with an error!";
        }
    });
}
