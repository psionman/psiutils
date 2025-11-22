from psiutils.utilities import invert


def test_invert():
    enum = {
        'a': 1,
        'b': 2,
    }
    enum = invert(enum)

    assert enum[1] == 'a'
    assert enum['b'] == 2
