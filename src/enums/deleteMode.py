from enum import Enum

class DeleteMode(str, Enum):
    CASCADE = "cascade"
    REASSIGN = "reassign"