import SVG from "svg.js"

let draw = SVG('drawing').viewbox(0, 0, 100, 100);
export function drawFromActions(actions) {
    console.log(actions);
    draw.clear();
    for (let [shapeId, command, value] of actions) {
        if (command === "created") {
            draw[value[0]](...value.slice(1)).id(shapeId);
        } else {
            SVG.get(shapeId)[command](value);
        }
    }
}
