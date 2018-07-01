from copy import deepcopy
import re

_shrew_actions__ = []
RAINBOW = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']


class animation:
    def __init__(self, duration=1):
        self.duration = duration

    def __enter__(self):
        _shrew_actions__.append((None, 'animation', [self.duration]))

    def __exit__(self, *args):
        _shrew_actions__.append((None, 'animation-end', [self.duration]))


class AbstractShape:
    _shape_count__ = 0
    _shape_type__ = None
    _default_arguments__ = {
        'x': 50,
        'y': 50,
        'color': 'black',
        'transparency': 0,
        'rotation': 0,
    }
    # maps Shape properties to svg.js command names
    _commands_map__ = {
        'color': 'fill',
        'rotation': 'rotate',
        'points': 'plot',
        'x': 'cx',
        'y': 'cy',
    }

    # which properties should be passed to svg.js constructor
    _svg_constructor_arguments = []

    def __init__(self, copy_from=None, **kwargs):
        self.__dict__['_properties__'] = {}  # avoid calling __setattr__

        if copy_from is not None and not isinstance(copy_from, AbstractShape):
            raise TypeError("'{}' got an unexpected unnamed argument '{}'"
                            .format(self.__class__.__name__, copy_from))

        unknow_kwargs = set(kwargs.keys()).difference(set(self._default_arguments__.keys()))
        if unknow_kwargs:
            raise TypeError("'{}' got an unexpected keyword argument '{}'"
                            .format(self.__class__.__name__, unknow_kwargs.pop()))

        # Populate properties
        for property_name, default in self._default_arguments__.items():
            if copy_from is not None:
                default = deepcopy(copy_from._properties__[property_name])
            self._properties__[property_name] = deepcopy(kwargs.get(property_name, default))

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
                self._log_action__(name, value, initial=True)

    def copy(self, **kwargs):
        return self.__class__(copy_from=self, **kwargs)

    def _log_action__(self, command, value, initial=False):
        # Corrections
        command = self._commands_map__.get(command, command)

        if command == 'transparency':
            command = 'opacity'
            value = 1 - value / 100

        _shrew_actions__.append((self.__id, command, value, initial))

        # Correct cx, cy
        if command in ['width', 'font']:
            self._log_action__('x', self.x, initial)
        if command in ['height', 'font']:
            self._log_action__('y', self.y, initial)

    def flip_horizontal(self):
        self._log_action__("flip", "y")

    def flip_vertical(self):
        self._log_action__("flip", "x")

    def __getattr__(self, name):
        try:
            return self._properties__[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self._properties__:
            value = deepcopy(value)
            self._properties__[name] = value
            self._log_action__(name, value)
        elif name is self.__dict__ or name.startswith('_'):
            self.__dict__[name] = value
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __str__(self):
        color = self.color
        name = " ".join(re.findall('[A-Za-z][^A-Z]*', self.__class__.__name__)).lower()

        if not isinstance(self.color, str):
            if len(color) == 1:
                color = color[0]
            elif len(color) == 0:
                color = ''
            else:
                color = " and ".join([", ".join(color[:-1]), color[-1]])
        return "{color} {shape}".format(color=color, shape=name)


class AbstractShapeWidthHeight(AbstractShape):
    _default_arguments__ = deepcopy(AbstractShape._default_arguments__)
    _default_arguments__.update({
        'width': 100,
        'height': 100,
    })

    def enlarge(self, multiply):
        self.width *= multiply
        self.height *= multiply


class AbstractShapePoints(AbstractShape):
    _default_arguments__ = deepcopy(AbstractShape._default_arguments__)
    _default_arguments__.update({
        'points': [0, 0, 100, 100],
        'width': None,
        'height': None,
        'x': None,
        'y': None,
    })

    def __init__(self, points=None, **kwargs):
        copy_from = kwargs.pop('copy_from', None)
        kwargs['points'] = points
        AbstractShape.__init__(self, copy_from=copy_from, **kwargs)


class Rectangle(AbstractShapeWidthHeight):
    _shape_type__ = 'rect'
    _svg_constructor_arguments = ['width', 'height']


Square = Rectangle


class Ellipse(AbstractShapeWidthHeight):
    _shape_type__ = 'ellipse'
    _svg_constructor_arguments = ['width', 'height']


Circle = Ellipse


class Line(AbstractShapePoints):
    _shape_type__ = 'line'
    _svg_constructor_arguments = ['points']

    def _log_action__(self, command, value, initial=False):
        if command == 'color':
            command = 'stroke'
        AbstractShapeWidthHeight._log_action__(self, command, value, initial)


class Polygon(AbstractShapePoints):
    _shape_type__ = 'polygon'
    _svg_constructor_arguments = ['points']

    _default_arguments__ = deepcopy(AbstractShapePoints._default_arguments__)
    _default_arguments__.update({
        'points': [(50,0), (0,100), (100,100)],
    })


class Path(AbstractShapeWidthHeight):
    _shape_type__ = 'path'
    _svg_constructor_arguments = ['path']
    _default_arguments__ = deepcopy(AbstractShapeWidthHeight._default_arguments__)
    _default_arguments__.update({
        'path': "M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zM262.655 90c-54.497 0-89.255 22.957-116.549 63.758-3.536 5.286-2.353 12.415 2.715 16.258l34.699 26.31c5.205 3.947 12.621 3.008 16.665-2.122 17.864-22.658 30.113-35.797 57.303-35.797 20.429 0 45.698 13.148 45.698 32.958 0 14.976-12.363 22.667-32.534 33.976C247.128 238.528 216 254.941 216 296v4c0 6.627 5.373 12 12 12h56c6.627 0 12-5.373 12-12v-1.333c0-28.462 83.186-29.647 83.186-106.667 0-58.002-60.165-102-116.531-102zM256 338c-25.365 0-46 20.635-46 46 0 25.364 20.635 46 46 46s46-20.636 46-46c0-25.365-20.635-46-46-46z",
    })


class Text(AbstractShape):
    _shape_type__ = 'text'
    _svg_constructor_arguments = ['text']

    _default_arguments__ = deepcopy(AbstractShape._default_arguments__)
    _default_arguments__.update({
        'text': "Hello World!",
        'font_size': 10,
    })

    def __init__(self, text=None, **kwargs):
        copy_from = kwargs.pop('copy_from', None)
        kwargs['text'] = str(text)
        AbstractShape.__init__(self, copy_from=copy_from, **kwargs)

    def _log_action__(self, command, value, initial=False):
        if command == 'font_size':
            command = 'font'
            value = ['size', value]
        elif command == 'text':
            value = str(value)
        AbstractShape._log_action__(self, command, value, initial)

    def enlarge(self, multiply):
        self.font_size *= multiply
