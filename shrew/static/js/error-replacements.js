let replacements = {
    "SyntaxError: bad token": "SyntaxError: something's wrong with the structure of this line",
};

export default function replaceError(message) {
    if (replacements[message] !== undefined) {
        return replacements[message];
    }
    return message;
}
