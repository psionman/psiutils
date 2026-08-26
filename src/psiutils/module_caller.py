class ModuleCaller:
    def __init__(self, root, parsed_args: dict) -> None:
        self.modules["list"] = (self._list, "List module definitions")
        self.args = parsed_args
        if self._select_module():
            self.root = root
            self.root.after(100, self._run_module)
        else:
            root.destroy()

    def _select_module(self) -> bool:
        """Return True if a valid, runnable module was selected."""
        module = self.args.module
        if module in ("list", None) or module not in self.modules:
            if module not in ("list", None):
                print(f"*** Invalid function name: {module} ***")
            self._list()
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

    def _list(self) -> None:
        keys = sorted(self.modules.keys())
        padding = max(len(key) for key in keys)
        for key in keys:
            _, help_text = self.modules[key]
            if help_text:
                print(f"{key:.<{padding}} {help_text}")
            else:
                print(key)
