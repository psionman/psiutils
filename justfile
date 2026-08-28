package_name := `basename $(pwd)`

list:
    just --list

version:
    uv run python -c "from {{package_name}} import __version__; print(__version__)"

test arg1="" arg2="":
    uv run -m pytest {{arg1}} {{arg2}}
