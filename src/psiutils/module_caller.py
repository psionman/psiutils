# module_caller.py
import argparse


class ModuleCaller:
    def __init__(self, root, parsed_args: dict) -> None:
        self.modules["modules"] = (
            self._list_modules,
            "List module definitions",
        )
        self.args = parsed_args
        if self._select_module():
            self.root = root
            self.root.after(100, self._run_module)
        else:
            root.destroy()

    def _select_module(self) -> bool:
        """Return True if a valid, runnable module was selected."""
        module = self.args.module
        if module in ("modules", None) or module not in self.modules:
            if module not in ("modules", None):
                print(f"*** Invalid module name: {module} ***")
            self._list_modules()
            return False
        return True

    def _run_module(self) -> None:
        try:
            self.modules[self.args.module][0]()
        except ValueError as e:
            print(f"Error running module: {e}")
        finally:
            self.root.destroy()

    def _require(self, attr: str, message: str) -> str:
        """Return the named CLI arg, or raise ValueError if missing."""
        value = getattr(self.args, attr)
        if not value:
            raise ValueError(message)
        return value

    def _list_modules(self) -> None:
        keys = sorted(self.modules.keys())
        padding = max(len(key) for key in keys) + 3
        for key in keys:
            _, help_text = self.modules[key]
            if help_text:
                print(f"{key:.<{padding}} {help_text}")
            else:
                print(key)

    @classmethod
    def create_parser(cls, arg_definitions) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        for arg in arg_definitions:
            parser.add_argument(arg[0], nargs="?", default=None, help=arg[1])
        return parser.parse_args()
