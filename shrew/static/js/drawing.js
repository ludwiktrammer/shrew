import SVG from "svg.js"
import cssColors from "css-color-names";

let draw = SVG('drawing').viewbox(0, 0, 100, 100);
export function drawFromActions(actions) {
    draw.clear();

    let animation;

    // for each element we should only use a single animation object
    // per animation block. So we keep past animation objects here.
    let animationCache = {};

    for (let [shapeId, command, value, initial] of actions) {
        if (command === "created") {
            let shape = draw[value[0]](...value.slice(1)).id(shapeId);
            if (animation) {
                shape.opacity(0);
            }
        } else if (command === "animation") {
            animation = {
                duation: value[0] * 1000,
            };
        } else if (command === "animation-end") {
            animation = undefined;
            animationCache = {};
        } else {
            if (['fill', 'stroke'].includes(command)) {
                if (Array.isArray(value)) {
                    value = createGradient(value);
                } else {
                    value = getColorFromName(value);
                }
            }
            let shape = SVG.get(shapeId);
            if (animation && (!initial || command === "opacity")) {
                if (animationCache[shapeId]) {
                    shape = animationCache[shapeId];
                } else {
                    shape = shape.animate(animation.duation);
                    animationCache[shapeId] = shape;
                }
            }
            shape[command](value);
        }
    }
}

function createGradient(colors) {
    return draw.gradient("linear", (stop) => {
        for (let [i, color] of colors.entries()) {
            stop.at((1 / (colors.length - 1)) * i, getColorFromName(color));
            console.log((1 / (colors.length - 1)) * i);
        }
    }).from(0, 0).to(0, 1);
}


function getColorFromName(color) {
    return cssColors[color] || color;
}
