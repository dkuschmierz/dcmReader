"""Definition of DCM function"""
from dataclasses import dataclass


@dataclass
class DcmFunction:
    """Definition of a function

    Attributes:
        name (str):         Name of the function
        version (str):      Version number of the function
        description (str):  Description of the function
    """

    name = None
    description = None
    version = None

    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    def __str__(self):
        return f'FKT {self.name} "{self.version}"  "{self.description}"'

    def __lt__(self, other):
        return self.name < other.name
