from copy import deepcopy

_shrew_actions__ = []


class AbstractShape:
    _shape_count__ = 0
    _shape_type__ = None
    _default_arguments__ = {
        'x': 0,
        'y': 0,
        'color': 'black',
        'width': 100,
        'height': 100,
        'transparency': 0,
        'rotation': 0,
    }
    # which properties should be passed to svg.js constructor
    _svg_constructor_arguments = []

    def __init__(self, copy_from=None, **kwargs):
        self.__dict__['_properties__'] = {}  # avoid calling __setattr__

        unknow_kwargs = set(kwargs.keys()).difference(set(self._default_arguments__.keys()))
        if unknow_kwargs:
            raise TypeError("'{}' got an unexpected keyword argument '{}'"
                            .format(self.__class__.__name__, unknow_kwargs.pop()))

        # Populate properties
        for property, default in self._default_arguments__.items():
            if copy_from is not None:
                default = deepcopy(copy_from._properties__[property])
            self._properties__[property] = kwargs.get(property, default)

        self._log__init()

    def _log__init(self):
        """
        Logs shape creation and all its properties.
        """
        # Get a unique id for the shape
        AbstractShape._shape_count__ += 1
        self.__id = 'shape{}'.format(AbstractShape._shape_count__)

        # Gather constructor arguments and log creation
        log_args = [self._shape_type__]
        for name in self._svg_constructor_arguments:
            log_args.append(self._properties__[name])
        self._log_action__('created', log_args)

        # Log the rest of the properties
        for name, value in self._properties__.items():
            if name not in self._svg_constructor_arguments:
                self._log_action__(name, value)

    def copy(self, **kwargs):
        return self.__class__(copy_from=self, **kwargs)

    def _log_action__(self, action, value):
        # Corrections
        if action == 'color':
            action = 'fill'
        if action == 'transparency':
            action = 'opacity'
            value = 1 - value / 100
        if action == 'rotation':
            action = 'rotate'
        if action == 'points':
            action = 'plot'
        _shrew_actions__.append((self.__id, action, value))

    def flipHorizontal(self):
        _shrew_actions__.append((self.__id, "flip", "y"))

    def flipVertical(self):
        _shrew_actions__.append((self.__id, "flip", "x"))

    def __getattr__(self, name):
        try:
            return self._properties__[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self._properties__:
            self._properties__[name] = value
            self._log_action__(name, value)
        else:
            self.__dict__[name] = value


class AbstractShapePoints(AbstractShape):
    _default_arguments__ = deepcopy(AbstractShape._default_arguments__)
    _default_arguments__.update({
        'points': [0, 0, 100, 100],
        'width': None,
        'height': None,
        'x': None,
        'y': None,
    })

class Rectangle(AbstractShape):
    _shape_type__ = 'rect'
    _svg_constructor_arguments = ['width', 'height']


Square = Rectangle


class Ellipse(AbstractShape):
    _shape_type__ = 'ellipse'
    _svg_constructor_arguments = ['width', 'height']


Circle = Ellipse


class Line(AbstractShapePoints):
    _shape_type__ = 'line'
    _svg_constructor_arguments = ['points']

    def _log_action__(self, action, value):
        if action == 'color':
            action = 'stroke'
        AbstractShape._log_action__(self, action, value)

class Polygon(AbstractShapePoints):
    _shape_type__ = 'polygon'
    _svg_constructor_arguments = ['points']


class Text(AbstractShape):
    _shape_type__ = 'text'
    _svg_constructor_arguments = ['text']

    _default_arguments__ = deepcopy(AbstractShape._default_arguments__)
    _default_arguments__.update({
        'text': "Example text",
    })
