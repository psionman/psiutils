
from psiutils.errors import ErrorMsg, ERROR, NO_MESSAGE


def test_null():
    error = ErrorMsg()
    assert error.header == ERROR
    assert error.message == NO_MESSAGE
