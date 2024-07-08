from pathlib import Path


class FsScanner:
    def __init__(self):
        self.target_types: list[str] = []
        self.forbidden_prefixes: list[str] = []
        self.forbidden_suffixes: list[str] = []

    def forbidden(self, filename: str) -> bool:
        return any(filename.startswith(prefix) for prefix in self.forbidden_prefixes) or \
            any(filename.endswith(suffix)
                for suffix in self.forbidden_suffixes)

    def desired(self, filename: str) -> bool:
        if self.forbidden(filename):
            return False

        if len(self.target_types) == 0:
            return True

        return any(filename.endswith(suffix) for suffix in self.target_types)

    def add_target_type(self, type: str) -> None:
        if type not in self.target_types:
            self.target_types.append(type)

    def add_forbidden_prefix(self, prefix: str) -> None:
        if prefix not in self.forbidden_prefixes:
            self.forbidden_prefixes.append(prefix)

    def add_forbidden_suffix(self, suffix: str) -> None:
        if suffix not in self.forbidden_suffixes:
            self.forbidden_suffixes.append(suffix)

    def get_subdirs(self, dir: Path) -> list[Path]:
        try:
            res: list[Path] = []

            for name in dir.glob("*"):
                if not name.is_dir():
                    continue

                if self.forbidden(name.stem):
                    continue

                res.append(name)

            return sorted(res)
        except:
            return []

    def scan_dir(self, dir: Path | str) -> list[Path]:
        dir = Path(dir)

        res: list[Path] = []

        for filename in dir.glob("*"):
            if not filename.is_file():
                continue

            if self.desired(filename.name):
                res.append(filename)

        subdirs = self.get_subdirs(dir)
        for subdir in subdirs:
            res += self.scan_dir(subdir)

        return res
