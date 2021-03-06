#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
"""Auto python property creation."""
import sys
import collections
import inspect
from .MooseException import MooseException


class Property(object):
    """
    A descriptor object for creating properties for the AutoPropertyMixin class defined below.

    A system using this object and the AutoPropertyMixin class was created to allow for dynamic
    property creation on objects that allows defaults, types, and a required status to be defined
    for the properties.

    When developing the tokens it was desirable to create properties (via @property) etc. to access
    token data, but it became a bit tedious so an automatic method was created, see the
    documentation on the AutoPropertyMixin class for information on using the automatic system.

    This property class can also be inherited from to allow for arbitrary checks to be performed,
    for example that a number is positive or a list is the correct length.

    NOTE: Generally, this class is not intended to be used directly.
    """
    def __init__(self, name, default=None, ptype=None, required=False):
        self.__name = name
        self.__type = ptype
        self.__required = required
        self.__default = default

        if (ptype is not None) and (not isinstance(ptype, type)):
            msg = "The supplied property '{}' type (ptype) must be of type 'type', but '{}' provided."
            raise MooseException(msg, name, type(ptype).__name__)

        if (ptype is not None) and (default is not None) and (not isinstance(default, ptype)):
            msg = "The default for property '{}' must be of type '{}', but '{}' was provided."
            raise MooseException(msg, name, ptype.__name__, type(default).__name__)

    @property
    def name(self):
        """Return the name of the property."""
        return self.__name

    @property
    def default(self):
        """Return the default for this property."""
        return self.__default

    @property
    def type(self):
        """The required property type."""
        return self.__type

    @property
    def required(self):
        """Return the required status for the property."""
        return self.__required

    def __set__(self, instance, value):
        """Set the property value."""
        if instance._AutoPropertyMixinBase__mutable:
            self.onPropertySet(instance, value)
            instance._AutoPropertyMixinBase__properties[self.name] = value
        else:
            raise MooseException("The {} object is immutable, see mooseuitls.AutoPropertyMixin.",
                                 type(instance).__name__)

    def __get__(self, instance, owner):
        """Get the property value."""
        self.onPropertyGet(instance)
        return instance._AutoPropertyMixinBase__properties.get(self.name, self.default)

    def onPropertySet(self, instance, value):
        """
        Override this method to perform custom checks on set.

        NOTE: To maintain the existing checks, the base class method should be called.
        """
        if (self.__type is not None) and (not isinstance(value, self.__type)) and (value
                                                                                   is not None):
            msg = "The supplied property '{}' must be of type '{}', but '{}' was provided."
            raise MooseException(msg, self.name, self.type.__name__, type(value).__name__)

    def onPropertyGet(self, instance):
        """
        Override this method to perform custom checks on get.

        NOTE: To maintain the existing checks, the base class method should be called.
        """
        pass

    def onPropertyCheck(self, instance):
        """
        Perform checks on the properties.

        NOTE: To maintain the existing checks, the base class method should be called.
        """
        if self.required and (instance._AutoPropertyMixinBase__properties[self.name] is None):
            raise MooseException("The property '{}' is required.", self.name)


def addProperty(*args, **kwargs):
    """Decorator for adding properties."""
    def create(cls):
        """
        Method for creating and adding properties to the class.

        Use the "cls" keyword to set a custom Property class, for example:
            @addProperty('foo', cls=MyCustomProperty)
        """
        property_class = kwargs.pop('cls', Property)
        prop = property_class(*args, **kwargs)

        if not isinstance(prop, Property):
            msg = "The created object must be a 'Property' object but '{}' created."
            raise TypeError(msg.format(type(prop)))
        _init_properties(cls, prop)
        return cls

    return create


def _init_properties(cls, *props):
    """Helper method for adding descriptors to a class (not instance)."""

    properties = set()
    for sub_cls in inspect.getmro(cls):
        properties.update(AutoPropertyMixin.__DESCRIPTORS__[sub_cls])
    for prop in props:
        properties.add(prop)
        setattr(cls, prop.name, prop)

    cls.__DESCRIPTORS__[cls].update(properties)
    cls.__INITIALIZED__.add(cls)


class AutoPropertyMixinBase(object):
    """
    Base for AutoPropertyMixin that doesn't contain automatic attribute, which allows it to work
    moosetree.Node.
    """

    #: Storage for Property object descriptors, this should not be messed with.
    __DESCRIPTORS__ = collections.defaultdict(set)
    __INITIALIZED__ = set()

    def __init__(self, mutable=True, **kwargs):

        # A flag for controlling the mutability of the object
        self.__mutable = True  # must be True initially to allow for the properties to initialize

        # Class members
        self.__properties = dict()  # storage for property values, addProperty items

        # Initialize properties, this happens automatically if addProperty decorator is used,
        # but when it is not the properties from the parent classes need to get added.
        if self.__class__ not in self.__INITIALIZED__:
            _init_properties(self.__class__)

        descriptors = self.__DESCRIPTORS__[self.__class__]
        for prop in descriptors:
            setattr(self.__class__, prop.name, prop)
            self.__properties[prop.name] = prop.default

        # Update the properties from the key value pairs
        self.update(kwargs)

        # Check properties
        for prop in descriptors:
            prop.onPropertyCheck(self)

        # Update the mutable flag
        self.__mutable = mutable

    def __setstate__(self, state):
        """
        Re-create the properties after a pickle load.
        """
        self.__dict__ = state
        for key, value in self.__properties.items():
            setattr(self, key, value)

    def update(self, other):
        """
        Update properties given a dict-like object.
        """
        for key, value in other.items():
            key = key.strip('_')
            if value is None:
                continue
            if key in self.__properties:
                setattr(self, key, value)


class AutoPropertyMixin(AutoPropertyMixinBase):
    """
    Class mixin to add automatic property setter/getters that support type restrictions.

    In many cases it is useful to create objects with properties that have setters and getters so
    that sanity and type checks can be performed, such as follows:

    class Foo(object):
       def __init__(self):
           self.__foo = None

       @property
       def foo(self):
          # ... to some sanity checks of the class here ...
          return self.__foo

       @foo.setter
       def foo(self, value):
           # ... do some fancy type checking here...
           self.__foo = value

    The AutoPropertyMixin class allows for arbitrary properties to be defined via the
    @addProperty decorator, this decorator will automatically add the correct setters and
    getters for the property that includes type checking among other features (see Property).

    For example properties, in the python sense, may be created using the class PROPERTIES variable.
    For example,

        @addProperty('foo', required=True)
        class Example(AutoPropertyMixin):
            ...
        node = Example(foo=42)
        node.foo = 43

    The properties from all parent classes are automatically retrieved and construction.

    Additionally, arbitrary attributes can be stored on creation or by using the dict() style
    set/get methods. By convention any leading or trailing underscores used in defining the
    attribute in the constructor are removed for storage.

        node = Example(foo=42, range_=[0,2])
        node['range'] = [0, 1]

    Inputs:
        mutable[bool]: (default: True) Set the object to be mutable/immutable.
        kwargs: (Optional) Any key, value pairs supplied are stored as properties or attributes.
    """
    def __init__(self, *args, **kwargs):
        self.__attributes = dict()  # storage for attributes (i.e., unknown key, values)
        AutoPropertyMixinBase.__init__(self, *args, **kwargs)

    @property
    def attributes(self):
        """
        Return the dict() of attributes.
        """
        if self._AutoPropertyMixinBase__mutable:
            return self.__attributes
        else:
            raise MooseException("The {} object is immutable, see mooseuitls.AutoPropertyMixin.",
                                 type(self).__name__)

    def update(self, other):
        """
        Update properties and attributes given a dict-like object.
        """
        for key, value in other.items():
            key = key.strip('_')
            if value is None:
                continue
            if key in self._AutoPropertyMixinBase__properties:
                setattr(self, key, value)
            else:
                self.__attributes[key] = value

    def get(self, *args):
        """
        Return an attribute with optional default
        """
        return self.__attributes.get(*args)

    def __getitem__(self, key):
        """
        Return an attribute.
        """
        return self.__attributes[key]

    def __setitem__(self, key, value):
        """
        Create/set an attribute.
        """
        if self._AutoPropertyMixinBase__mutable:
            self.__attributes[key] = value
        else:
            raise MooseException("The {} object is immutable, see mooseuitls.AutoPropertyMixin.",
                                 type(self).__name__)

    def __contains__(self, key):
        """
        Allow for "in" operator to check for attributes.
        """
        return key in self.__attributes
