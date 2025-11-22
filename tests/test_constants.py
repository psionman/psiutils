from psiutils.constants import DIALOG_STATUS


def test_dialog_status() -> None:
    assert DIALOG_STATUS['yes'] is True
    assert DIALOG_STATUS[1] == 'exit'
