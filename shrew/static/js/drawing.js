import SVG from "svg.js"
import cssColors from "css-color-names";

let draw = SVG('drawing').viewbox(0, 0, 100, 100);

// for each element we should only use a single animation object
// per animation block. So we keep past animation objects here.
let animationCache = {};
let timeoutObject;

export function drawFromActions(actions) {
    draw.clear();
    cancelAnimations();

    let animation;
    let hasAnimation = false;
    processAction(actions, 0);
    function processAction(actions, index) {
        if (index >= actions.length) {
            if (hasAnimation) {
                // loop
                drawFromActions(actions);
            }
            return;
        }
        let [shapeId, command, value, initial] = actions[index];
        if (command === "animation-end") {
            let animationObj = Object.values(animationCache)[0];
            let duration = animation.duration;

            function afterAnimationFinished() {
                animation = undefined;
                animationCache = {};
                processAction(actions, ++index);
            }

            if (animationObj !== undefined) {
                animationObj.after(afterAnimationFinished);
            } else {
                timeoutObject = setTimeout(afterAnimationFinished, duration);
            }
            return;
        }
        if (command === "created") {
            let shape = draw[value[0]](...value.slice(1)).id(shapeId);
            if (animation) {
                shape.opacity(0);
            }
        } else if (command === "animation") {
            hasAnimation = true;
            animation = {
                duration: value[0] * 1000,
            };
        } else if(['fill', 'stroke'].includes(command)) {
            // gradient support
            let shape = SVG.get(shapeId);
            if (!Array.isArray(value)) {
                value = [value];
            }
            let existingGradient = shape.reference(command);
            if (existingGradient) {
                updateGradient(value, existingGradient, animation);
            } else {
                let gradient = createGradient(value);
                shape[command](gradient);
            }
        } else {
            let shape = SVG.get(shapeId);
            if (animation && (!initial || command === "opacity")) {
                if (animationCache[shapeId]) {
                    shape = animationCache[shapeId];
                } else {
                    shape = shape.animate(animation.duration);
                    animationCache[shapeId] = shape;
                }
            }
            shape[command](value);
        }
        processAction(actions, ++index);
    }
}

function cancelAnimations() {
    for (let animation of Object.values(animationCache)) {
        animation.stop(false, true);
    }
    if (timeoutObject !== undefined) {
        clearTimeout(timeoutObject);
    }
    animationCache = {};
    timeoutObject = undefined;
}

function createGradient(colors) {
    return draw.gradient("linear", (stop) => {
        for (let [i, color] of colors.entries()) {
            stop.at(getGradientOffset(colors, i), getColorFromName(color));
        }
    }).from(0, 0).to(0, 1);
}

function updateGradient(colors, gradient, animation) {
    let previousNumOfStops = gradient.node.childNodes.length;
    let numOfStops = colors.length;

    let stop;
    for (let i = 0; i < numOfStops; i++) {
        let color = getColorFromName(colors[i]);
        stop = gradient.get(i);
        if(stop === null) {
            console.log(`created ${i}`);
            stop = gradient.at(1, color);
        }
        if (animation) {
            let stopId = stop.id();
            if (animationCache[stopId]) {
                stop = animationCache[stopId];
            } else {
                stop = stop.animate(animation.duration);
                animationCache[stopId] = stop;
            }
        }
        stop = stop.update(getGradientOffset(colors, i), color);
    }

    if (!animation || stop === undefined) {
        removeExtraStops();
    } else {
        stop.after(removeExtraStops);
    }

    function removeExtraStops() {
        for (let i = previousNumOfStops - 1; i >= numOfStops; i--) {
            let stop = gradient.get(i);
            gradient.removeElement(stop);
        }
    }
}

function getGradientOffset(colors, index) {
    if (colors.length === 1) {
        // this helps when animating additional colors via animation
        // since the value of 1 helps to initially cover the new colors
        return 1;
    }
    if (index >= colors.length) {
        // to be removed; hide for now
        return 1;
    }
    return (1 / (colors.length - 1)) * index;
}

function getColorFromName(color) {
    return cssColors[color] || color;
}
