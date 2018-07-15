import cssColors from "css-color-names";
import hexToRgb from "hex-to-rgb";

const $placeholder = document.getElementById("colors-table");

if ($placeholder) {
    let $columns = document.createElement("div");
    $columns.classList.add("columns", "is-multiline", "is-mobile", "has-text-centered", "has-text-weight-bold");
    $placeholder.appendChild($columns);

    for (let [name, color] of Object.entries(cssColors)) {
        let $column = document.createElement("div");
        $column.classList.add("column", "is-2-desktop", "is-3-tablet", "is-6-mobile");
        $column.style.backgroundColor = color;
        $column.classList.add(`has-text-${contrast(color)}`);
        $column.textContent = name;
        $columns.appendChild($column);
    }

    /**
     * Returns a value contrasting with the given color. Either "light" or "dark".
     */
    function contrast(hex) {
        let [red, green, blue] = hexToRgb(hex);
        let value = Math.sqrt(red * red * .241 + green * green * .691 + blue * blue * .068);

        return (value < 130) ? 'light' : 'dark';
    }
}
