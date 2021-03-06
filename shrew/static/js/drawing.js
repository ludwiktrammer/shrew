import SVG from "svg.js"
import cssColors from "css-color-names";

let draw = SVG('drawing').viewbox(0, 0, 100, 100);

// for each element we should only use a single animation object
// per animation block. So we keep past animation objects here.
let animationCache = {};
let timeoutObject;
let animation;
let hasAnimation;

// Specific handlers for different types of action
let actionHandlers = {
    "default": (shapeId, command, value, initial) => {
        let shape = getShape(shapeId, (animation && !initial));
        shape[command](value);
    },

    "created": (shapeId, command, value) => {
        if (value[0] === "line" || value[0] === "polyline") {
            value[1] = straightLineWorkAround(value[1]);
        }
        let shape = draw[value[0]](...value.slice(1)).id(shapeId);
        if (animation) {
            shape.opacity(0);
        }
    },

    "animation": (shapeId, command, value) => {
        hasAnimation = true;
        animation = {
            duration: value[0] * 1000,
        };
    },

    "animation-end": () => {
        let animationObj = Object.values(animationCache)[0];
        let duration = animation.duration;

        return new Promise((resolve, reject) => {
            if (animationObj !== undefined) {
                animationObj.after(resolve);
            } else {
                timeoutObject = setTimeout(resolve, duration);
            }
        }).then(() => {
            animation = undefined;
            animationCache = {};
        });
    },

    "attr": (shapeId, command, value, initial) => {
        let shape = getShape(shapeId, animation=(animation && !initial));
        shape[command](...value);
    },

    "font": (...args) => {
        actionHandlers.attr(...args);
    },

    "text": (shapeId, command, value, initial) => {
        let isAnimated = (animation && !initial);
        let shape = getShape(shapeId, (animation && !initial));
        if(!isAnimated) {
            shape[command](value);
        } else {
            // A pseudo-animation of text change
            const morph_hide = new SVG.MorphObj(shape.target().opacity(), 0);
            const morph_show = new SVG.MorphObj(0, shape.target().opacity());
            let new_text_present = false;
            shape.during(pos => {
                if (pos < 0.5) {
                    shape.target().opacity(morph_hide.at(pos * 2));
                } else {
                    if (!new_text_present) {
                        shape.target().text(value);
                        new_text_present = true;
                    }
                    shape.target().opacity(morph_show.at((pos - 0.5) * 2));
                }
            });
        }
    },

    "fill": (shapeId, command, value) => {
        let shape = getShape(shapeId);
        if (value === 'none') {
            shape[command](value);
            return;
        }
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
    },

    "stroke": (...args) => {
        actionHandlers.fill(...args);
    },

    "opacity": (shapeId, command, value) => {
        let shape = getShape(shapeId, !!animation);
        shape[command](value);
    },

    "plot": (shapeId, command, value, initial) => {
        value = straightLineWorkAround(value);
        actionHandlers.default(shapeId, command, value, initial);
    },
};

/**
 * The the actual drawing.
 * `afterInitialDraw` is a callback fired just before the first animation.
 */
export function drawFromActions(actions, afterInitialDraw) {
    draw.clear();
    cancelAnimations();
    animation = undefined;
    hasAnimation = false;

    processAction(actions, 0);

    if (afterInitialDraw) {
        afterInitialDraw(draw.svg(), hasAnimation);
    }

    function processAction(actions, index) {
        if (index >= actions.length) {
            if (hasAnimation) {
                // loop
                drawFromActions(actions);
            }
            return;
        }
        let [shapeId, command, value, initial] = actions[index];

        let handler_promise;
        if(command  in actionHandlers) {
            handler_promise = actionHandlers[command](shapeId, command, value, initial);
        } else {
            handler_promise = actionHandlers["default"](shapeId, command, value, initial);
        }

        if (handler_promise !== undefined) {
            // if handler returned a promise, wait for it
            handler_promise.then(() => {
                processAction(actions, ++index);
            })
        } else {
            processAction(actions, ++index);
        }
    }
}

/**
 * Returns the shape object or (if `isAnimated` is set to true)
 * an animation object associated with it.
 */
function getShape(shapeId, isAnimated=false) {
    let shape = SVG.get(shapeId);
    if (isAnimated) {
        if (animationCache[shapeId]) {
            shape = animationCache[shapeId];
        } else {
            shape = shape.animate(animation.duration);
            animationCache[shapeId] = shape;
        }
    }
    return shape;
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

/**
 * Works around this problem: https://stackoverflow.com/q/21638169/262618
 * (where SVG gradient doesn't work if a line is strictly vertical/horizontal)
 */
function straightLineWorkAround(points) {
    if (!Array.isArray(points) || points.length < 1 || !Array.isArray(points[0]) || points[0].length !== 2) {
        return points; // unsupported format, abort
    }
    let [firstX, firstY] = points[0];
    let differentX = false;
    let differentY = false;

    for (let point of points) {
        if (!Array.isArray(point) || point.length !== 2) {
            return points; // unsupported format, abort
        }
        let [x, y] = point;
        if (x !== firstX) {
            differentX = true;
        }
        if (y !== firstY) {
            differentY = true;
        }
    }

    if (!differentX) { // all points horizontal
        points[0][0] += 0.001;
    }
    if (!differentY) { // all points vertical
        points[0][1] += 0.001;
    }

    return points;
}
