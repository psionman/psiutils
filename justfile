list:
    just --list

test arg1="":
    uv run -m pytest {{arg1}}
