list:
    just --list

test arg1="" arg2="":
    uv run -m pytest {{arg1}} {{arg2}}
