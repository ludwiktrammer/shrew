@builtin "whitespace.ne"
@builtin "string.ne"

# Main
Main -> Declaration | Animation | ShapeAccess

# Shape macros
buildShape[shape, kwargs] -> _ $shape "(" buildArguments[$kwargs] ")"
buildArguments[kwargs] -> ( buildArgument[$kwargs] ):*
buildArgument[kwargs] -> _ $kwargs _ "=" _ Value _ ",":? _

# Declare Shape objects
Shape -> buildShape["Rectangle", WidthHeightKwargs]
Shape -> buildShape["Square", WidthHeightKwargs]
Shape -> buildShape["Ellipse", WidthHeightKwargs]
Shape -> buildShape["Circle", WidthHeightKwargs]
Shape -> buildShape["Line", PointsKwargs]
Shape -> buildShape["Polygon", PointsKwargs]
Shape -> buildShape["Text", TextKwargs]

# Declare other elements
Animation -> _ "with animation(" buildArguments[AnimationKwargs] "):" _

# Declare Kwargs
StandardKwargs -> "x" | "y" | "color" | "transparency" | "rotation"
WidthHeightKwargs -> StandardKwargs | "width" | "height"
PointsKwargs -> WidthHeightKwargs | "points"
TextKwargs -> StandardKwargs | "text" | "font_size"
AnimationKwargs -> "duration"

# Rules
Declaration -> Shape | _ Identifier _ "=" Shape
Value -> String | Number | Identifier | PropertyAccess
String -> dqstring | sqstring
Number -> "-":? [0-9.]:+
Identifier -> [a-zA-Z_] [a-zA-Z_]:*
PropertyAccess -> Identifier "." Identifier
