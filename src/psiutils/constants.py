"""Constants for the tkinter psiutils."""
from enum import Enum, auto

from .known_paths import get_documents_dir, get_downloads_dir

DEFAULT_GEOMETRY = '500x400'

DOCUMENTS_DIR = get_documents_dir()
DOWNLOADS_DIR = get_downloads_dir()

# GUI
PAD = 5
PADR = (0, PAD)
PADL = (PAD, 0)
PADT = (PAD, 0)
PADB = (0, PAD)

LARGE_FONT = ('Arial', 16)
BOLD_FONT = ('Arial', 12, 'bold')

# Colours
COLOURS = {
    'pale-umber': '#ffcfa0',
    'pale-red': '#ff9999',
    'pale-grey': '#e8e8e8'
}

CSV_FILE_TYPES = (
    ('csv files', '*.csv'),
    ('All files', '*.*')
)

TXT_FILE_TYPES = (
    ('csv files', '*.txt'),
    ('All files', '*.*')
)

XML_FILE_TYPES = (
    ('xml files', '*.xml'),
    ('All files', '*.*')
)


class Pad():
    W = (0, PAD)
    E = (PAD, 0)
    N = (PAD, 0)
    S = (0, PAD)


class Mode(Enum):
    VIEW = auto()
    NEW = auto()
    EDIT = auto()
    DELETE = auto()


class Status(Enum):
    YES = True
    NO = False
    CANCEL = None
    NULL = 0
    EXIT = 1
    OK = 2
    SUCCESS = 3
    UPDATED = 4
    ERROR = 5
    WARNING = 6
