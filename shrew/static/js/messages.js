// Make "close" buttons in messages work
let $closeButtons = document.querySelectorAll('.notification .delete');
for (let $button of $closeButtons) {
    $button.addEventListener('click', () => {
        $button.parentElement.classList.add("is-hidden");
    });
}
