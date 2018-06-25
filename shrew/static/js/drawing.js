import SVG from "svg.js"

let draw = SVG('drawing').viewbox(0, 0, 100, 100);
export function drawFromActions(actions) {
    console.log(actions);
    draw.clear();
    for (let [shapeId, command, value] of actions) {
        if (command === "created") {
            draw[value[0]](...value.slice(1)).id(shapeId);
        } else {
            if (['fill', 'stroke'].includes(command) && Array.isArray(value)) {
                value = createGradient(value);
            }
            SVG.get(shapeId)[command](value);
        }
    }
}

function createGradient(colors) {
    return draw.gradient("linear", (stop) => {
        for (let [i, color] of colors.entries()) {
            stop.at((1 / (colors.length - 1)) * i, color);
            console.log((1 / (colors.length - 1)) * i);
        }
    }).from(0, 0).to(0, 1);
}
