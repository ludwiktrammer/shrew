import { fas } from "@fortawesome/free-solid-svg-icons";


global.$builtinmodule = function(name)
{
    let shrew = Sk.importModule("shrew", false, false);
    let copy = Sk.importModule("copy", false, false);

    let modProxy = {
        get: function(obj, prop) {
            return buildAwesomeClass(prop);
        }
    };
    let mod = new Proxy({}, modProxy);

    /**
     * Dynamically creates a Shape Class for the requested icon.
     */
    function buildAwesomeClass(iconName) {
        let faIconName = 'fa' + iconName;
        if (fas[faIconName] === undefined) {
            return undefined;
        }
        let iconPath = fas[faIconName].icon[4];

        return Sk.misceval.buildClass(mod, function($gbl, $loc) {
            $loc._default_arguments__ = Sk.misceval.callsim(copy.$d['deepcopy'], shrew.$d['Path']._default_arguments__);
            $loc._default_arguments__.mp$ass_subscript(
                Sk.builtin.str('path'),
                Sk.builtin.str(iconPath)
            );
        }, iconName, [shrew.$d['Path']]);
    }

    return mod;
};
