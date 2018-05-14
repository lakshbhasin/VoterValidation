"""
Common functions and constants that are shared across multiple files.
"""

import inspect
import json
import logging
from enum import Enum

from django.http import HttpResponse


# Mapping between Master Voter File field name and Voter fields.


logger = logging.getLogger(__name__)


class ChoiceEnum(Enum):
    """
    A way of adapting Enums for Django neatly. See http://goo.gl/MAUtfQ to
    find usage (including how to use this with filter functions).
    """
    @classmethod
    def choices(cls):
        # Get all members of the class and filter down to properties
        members = inspect.getmembers(cls, lambda m: not inspect.isroutine(m))
        props = [m for m in members if m[0][:2] != '__']

        # Format into Django choice tuple. We replace "_" with " " in property
        # names and capitalize first letters.
        choices = tuple([(str(p[1].value),
                          p[0].replace("_", " ").title())
                         for p in props])
        return choices


def create_json_response(data, status=200):
    """
    Creates an HTTPResponse that represents a JSONified dict.
    :param data:
    :param status:
    :return: HTTPResponse
    """
    return HttpResponse(
        json.dumps(data),
        status=status,
        content_type="application/json")


def bad_request(message="Bad Request"):
    """
    Creates an HTTPResponse response which represents a bad request.
    """
    return create_json_response(data={'error': message}, status=400)
