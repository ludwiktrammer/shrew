import CodeMirror from "codemirror-minified";
import nearley from "nearley";

const grammar = nearley.Grammar.fromCompiled(global.grammar)

export default function autocomplete(cm) {
    const cursor = cm.getCursor();
    const line = cm.getLine(cursor.line);

    const afterCursor = line.substr(cursor.ch);
    if (["", ")", "):"].includes(afterCursor)) {
        const parser = new nearley.Parser(grammar);
        let list = [];
        parser.feed(line);
        let tableEntries = parser.table[parser.table.length - 1].scannable;
        for (let entry of tableEntries) {
            console.log(entry);
            let rule = entry.rule;
            let nameParts = rule.name.split("$");
            console.log(nameParts);
            if (nameParts.length >= 2 && nameParts[nameParts.length-2] === "string") {
                console.log(cursor.ch - entry.dot);
                list.push({
                    text: rule.symbols.map(s => s.literal).join(""),
                    from: CodeMirror.Pos(cursor.line, cursor.ch - entry.dot),
                    to: CodeMirror.Pos(cursor.line, cursor.ch),
                });
            }
        }


        return {
            list: list,
        };
    }
}
