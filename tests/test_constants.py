from pathlib import Path
import pytest
import re

from psiutils.constants import (
    Mode, Status, COLOURS, DEFAULT_GEOMETRY, DOCUMENTS_DIR, DOWNLOADS_DIR,
    PAD, PADR, PADL, PADT, PADB, CSV_FILE_TYPES, TXT_FILE_TYPES, XML_FILE_TYPES
    )


def test_mode_all_members_exist():
    expected = {"VIEW", "NEW", "EDIT", "DELETE"}
    assert {member.name for member in Mode} == expected


def test_mode_values_are_sequential():
    assert [m.value for m in Mode] == [1, 2, 3, 4]


def test_mode_members_immutable():
    with pytest.raises(AttributeError):
        Mode.VIEW = 99


def test_mode_comparison():
    assert Mode.VIEW is Mode.VIEW
    assert Mode.VIEW is not Mode.NEW


def test_mode_iteration_order():
    assert [m.name for m in Mode] == ["VIEW", "NEW", "EDIT", "DELETE"]


def test_mode_used_in_condition():
    mode = Mode.DELETE
    result = "deleting" if mode == Mode.DELETE else "other"
    assert result == "deleting"


# def test_status_all_members_exist():
#     expected = {
#         "YES", "NO", "CANCEL", "NULL", "EXIT",
#         "OK", "SUCCESS", "UPDATED", "ERROR", "WARNING"
#     }
#     print(f"{[member.name for member in Status]=}")
#     assert {member.name for member in Status} == expected
#     assert len(Status) == 10


def test_status_values_correct():
    assert Status.YES.value is True
    assert Status.NO.value is False
    assert Status.CANCEL.value is None
    assert Status.NULL.value == 0
    assert Status.EXIT.value == 1
    assert Status.OK.value == 2
    assert Status.SUCCESS.value == 3
    assert Status.UPDATED.value == 4
    assert Status.ERROR.value == 5
    assert Status.WARNING.value == 6


@pytest.mark.parametrize("member, value", [
    (Status.YES, True),
    (Status.NO, False),
    (Status.CANCEL, None),
    (Status.NULL, 0),
    (Status.EXIT, 1),
])
def test_status_lookup_by_value(member, value):
    assert Status(value) is member


def test_status_immutable():
    with pytest.raises(AttributeError):
        Status.YES = False

    with pytest.raises(AttributeError):
        Status.YES.value = 99


def test_status_in_condition():
    status = Status.SUCCESS
    result = "ok" if status in (Status.OK, Status.SUCCESS) else "other"
    assert result == "ok"


def test_colours_exist():
    assert 'pale-umber' in COLOURS
    assert 'pale-red' in COLOURS
    assert 'pale-grey' in COLOURS

    for colour in COLOURS.values():
        assert re.match(r'#[0-9a-fA-F]{6}\b', colour)


def test_geometry():
    assert 'x' in DEFAULT_GEOMETRY
    items = DEFAULT_GEOMETRY.split('x')
    assert items[0].isnumeric()
    assert items[1].isnumeric()


def test_dirs_exist():
    assert Path(DOCUMENTS_DIR).is_dir()
    assert Path(DOWNLOADS_DIR).is_dir()


def test_pad():
    assert isinstance(PAD, int)
    for item in [PADR, PADL, PADT, PADB]:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], int)
        assert isinstance(item[1], int)


@pytest.mark.parametrize(
    "file_types, expected_ext",
    [
        (CSV_FILE_TYPES, ".csv"),
        (TXT_FILE_TYPES, ".txt"),
        (XML_FILE_TYPES, ".xml"),
    ],
    ids=["CSV", "TXT", "XML"],
)
def test_file_types(file_types, expected_ext):
    # First entry: specific file type
    specific_desc, specific_pattern = file_types[0]
    desc_test = isinstance(specific_desc, str) and specific_desc.strip()
    pattern_test = (isinstance(specific_pattern, str)
                    and specific_pattern.startswith("*."))
    end_test = specific_pattern.endswith(expected_ext)
    assert desc_test, "Description must be non-empty string"
    assert pattern_test, "Pattern must start with *."
    assert end_test, f"Expected pattern to end with {expected_ext}"

    # Second entry: always "All files" with *.*
    all_desc, all_pattern = file_types[1]
    assert all_desc == "All files", "Second entry must be 'All files'"
    assert all_pattern == "*.*", "Second pattern must be '*.*'"


def test_all_file_types_have_all_files_entry():
    """Every file type tuple ends with the universal 'All files' entry"""
    for name, types_tuple in [
        ("CSV", CSV_FILE_TYPES),
        ("TXT", TXT_FILE_TYPES),
        ("XML", XML_FILE_TYPES),
    ]:
        assert types_tuple[-1] == ('All files', '*.*'), f"{name} missing standard 'All files' entry"
