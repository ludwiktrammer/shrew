import cssColors from "css-color-names";
import hexToRgb from "hex-to-rgb";

const $placeholder = document.getElementById("colors-table");

if ($placeholder) {
    let $columns = document.createElement("div");
    $columns.classList.add("columns", "is-multiline", "is-mobile", "has-text-centered", "has-text-weight-bold");
    $columns.style.marginTop = "0.75rem";
    $placeholder.appendChild($columns);

    for (let [name, color] of Object.entries(cssColors)) {
        let $column = document.createElement("div");
        $column.classList.add("column", "is-2-widescreen", "is-3-desktop", "is-4-tablet", "is-6-mobile");

        let $content = document.createElement("div");
        $content.style.backgroundColor = color;
        $content.classList.add("notification", `has-text-${contrast(color)}`);
        $content.textContent = name;
        $columns.appendChild($column);
        $column.appendChild($content);
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
