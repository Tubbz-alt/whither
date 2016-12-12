#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# object.py
#
# Copyright © 2016-2017 Antergos
#
# This file is part of whither.
#
# whither is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# whither is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# The following additional terms are in effect as per Section 7 of the license:
#
# The preservation of all legal notices and author attributions in
# the material or in the Appropriate Legal Notices displayed
# by works containing it is required.
#
# You should have received a copy of the GNU General Public License
# along with whither; If not, see <http://www.gnu.org/licenses/>.

""" Data descriptor objects to make data/settings easily accessible in all child classes. """

from threading import RLock


class AttributeDict(dict):
    """
    Dict subclass which provides access to its keys' values as attributes.

    See:
        dict.__doc__()

    """
    def __init__(self, seq=None, **kwargs):
        super().__init__(seq=seq, **kwargs)

        self['_lock'] = RLock()

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError()

    def __setattr__(self, attr, value):
        with self._lock:
            if isinstance(value, dict) and not isinstance(value, AttributeDict):
                # Make the value an AttributeDict
                value = AttributeDict(value)

            self[attr] = value

    def __setitem__(self, item, value):
        with self._lock:
            self[item] = value


class SharedData:
    """
    Descriptor that facilitates shared data storage/retrieval.

    Attributes:
        name      (str):  The name of the bound attribute.
        from_dict (dict): Initial data to store.

    """
    _data = dict()

    def __init__(self, name, from_dict=None):
        self.name = name

        if from_dict is not None:
            self._data[name] = AttributeDict(from_dict)

        elif name not in self._data:
            self._data[name] = None

    def __get__(self, instance, cls):
        val = self if self.name not in self._data else self._data[self.name]
        return val

    def __set__(self, instance, value):
        if self.name in self._data or self._data[self.name] is not None:
            raise AttributeError('SharedData attributes can only be assigned once!')

        self._data[self.name] = value


class NonSharedData:
    """
    Data descriptor that facilitates per-instance data storage/retrieval.

    Attributes:
        name      (str): The name of the bound attribute.

    """
    _data = dict()

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        val = self if not self._instance_data_check(instance) else self._data[instance.name]
        return val

    def __set__(self, instance, value):
        if not self._instance_data_check(instance):
            return

        self._data[instance.name] = value

    def _instance_data_check(self, instance):
        if instance is not None and instance.name not in self._data:
            self._data[instance.name] = None

        return instance is not None
