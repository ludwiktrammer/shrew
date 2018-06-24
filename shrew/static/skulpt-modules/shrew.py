_shrew_actions__ = []


class AbstractShape:
    _shape_count__ = 0
    shape_type = None

    def __init__(self, x=0, y=0, color='black', width=100, height=100):
        AbstractShape._shape_count__ += 1
        self.__id = 'shape{}'.format(AbstractShape._shape_count__)
        self._log_action__('created', self.shape_type)
        self._x = self._y = self._color = self._width = self._height = None

        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = color

    def _log_action__(self, action, value):
        _shrew_actions__.append((self.__id, action, value))

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val
        self._log_action__('x', val)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
        self._log_action__('y', val)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, val):
        self._color = val
        self._log_action__('fill', val)
        self._log_action__('stroke', val)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self._log_action__('width', val)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._height = val
        self._log_action__('height', val)


class AbstractShapePoints(AbstractShape):
    def __init__(self, x=0, y=0, color='black', width=100, height=100, points=None):
        AbstractShape.__init__(self, x, y, color, width, height)
        self._points = None
        if points is None:
            points = []
        self.points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, val):
        self._points = val
        self._log_action__('plot', val)


class Rectangle(AbstractShape):
    shape_type = 'rect'


Square = Rectangle


class Ellipse(AbstractShape):
    shape_type = 'ellipse'


Circle = Ellipse


class Line(AbstractShapePoints):
    shape_type = 'polyline'


class Polygon(AbstractShapePoints):
    shape_type = 'polygon'


class Text(AbstractShape):
    shape_type = 'text'

    def __init__(self, text="", x=0, y=0, color='black', width=100, height=100):
        AbstractShape.__init__(self, x, y, color, width, height)
        self._text = None
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = val
        self._log_action__('text', val)
