from pathlib import Path

from psiutils.known_paths import resolve_path


def test_resolve_path():
    path = Path(__file__).parent.parent
    assert resolve_path('__init__.py') == str(Path(path, '__init__.py'))
    assert resolve_path(Path('__init__.py')) == str(Path(path, '__init__.py'))
