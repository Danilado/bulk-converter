import platform
from modules.FsScanner import FsScanner
from modules.Converter import Converter
import os
from pathlib import Path


class App:
    def __init__(self) -> None:
        self.scanner = FsScanner()
        self.converter = Converter()
        self.running: bool = False

        self.menu_items = {
            1: ("Add file extension associations", self.add_target_types),
            2: ("Add forbidden prefixes", self.add_forbidden_prefixes),
            3: ("Add forbidden suffixes", self.add_forbidden_suffixes),
            4: ("Add target folders", self.add_target_folders),
            5: ("Add target folder (only one, supports whitespaces)", self.add_target_folder),
            6: ("Scan target folders for matching files", self.scan),
            7: ("Remove files from list by index", self.remove_by_indexes),
            8: ("Convert files in list", self.convert_all),
            9: ("Toggle delete originals", self.toggle_delete_orig),
            0: ("Exit", self.stop)
        }

        self.target_folders: list[Path] = []
        self.targets: list[Path] = []

        self.delete_originals: bool = False

    def toggle_delete_orig(self) -> None:
        self.delete_originals = not self.delete_originals

    def add_target_types(self) -> None:
        print(f"Input two or more file extensions first->from; other->to")
        data = input("> ").strip().split()

        if len(data) < 2:
            return

        types = [t if t.startswith(".") else "." + t for t in data]

        self.scanner.add_target_type(types[0])
        for t in types[1:]:
            self.converter.add_conversion(types[0], t)

    def add_forbidden_prefixes(self) -> None:
        print(f"Input prefixes (separated with spacebar)")
        print(f"Files and folders starting with prefix will be ignored")
        data = input("> ").strip().split()

        for prefix in data:
            self.scanner.add_forbidden_prefix(prefix)

    def add_forbidden_suffixes(self) -> None:
        print(f"Input suffixes (separated with spacebar)")
        print(f"Files and folders ending with suffix will be ignored")
        data = input("> ").strip().split()

        for suffix in data:
            self.scanner.add_forbidden_suffix(suffix)

    def add_target_folders(self) -> None:
        print(f"Input folder names to scan")
        data = input("> ").strip().split()

        for folder in data:
            fpath = Path(folder).resolve()
            if not fpath.exists():
                print(f"Folder {fpath} not found")
                continue
            if not fpath.is_dir():
                print(f"{fpath} is not a folder")
                continue
            if fpath in self.target_folders:
                print(f"{fpath} already in list")
                continue

            self.target_folders.append(fpath)

    def add_target_folder(self) -> None:
        print(f"Input folder name to scan")
        data = input("> ").strip()

        fpath = Path(data).resolve()
        if not fpath.exists():
            print(f"Folder {fpath} not found")
            return
        if not fpath.is_dir():
            print(f"{fpath} is not a folder")
            return
        if fpath in self.target_folders:
            print(f"{fpath} already in list")
            return

        self.target_folders.append(fpath)

    def scan(self) -> None:
        if len(self.target_folders) == 0:
            print(f"No folders to scan")
            return

        for folder in self.target_folders:
            res = self.scanner.scan_dir(folder)
            print(f"{folder} - {len(res)} matching files")

            for file in res:
                if file in self.targets:
                    print(f"{file} already in list")
                else:
                    self.targets.append(file)

        self.target_folders = []

        for target in self.targets:
            self.converter.resolve_file(target)

    def list_targets(self) -> None:
        self.converter.print_conversions()

    def remove_by_indexes(self) -> None:
        if len(self.targets) == 0:
            print(f"List already empty")
            return

        self.list_targets()
        data = input(
            "Input indexes of files to remove from list\n> ").strip().split()

        rmlist: list[int] = []
        for entry in data:
            try:
                n = int(entry)
                if n > 0 and n <= len(self.converter.conversions) and n - 1 not in rmlist:
                    rmlist.append(n - 1)
            except ValueError:
                continue

        self.converter.remove_conversions(rmlist)

    def convert_all(self) -> None:
        rc = self.converter.convert_all()

        print(f"Finished converting with {rc} errors")

        if not rc and self.delete_originals:
            for target in self.targets:
                try:
                    delete_file(target)
                except:
                    ...

        self.targets = []

    def print_menu(self) -> None:
        for key in self.menu_items.keys():
            print(f"{key}:\t{self.menu_items[key][0]}")

    def print_status(self) -> None:
        print(f"Delete original files: {self.delete_originals}")

        print(f"Target file extensions:")
        if len(self.scanner.target_types) == 0:
            print("\tAny")
        else:
            for text in self.scanner.target_types:
                print(f"\t{text}")

        print(f"Forbidden prefixes:")
        if len(self.scanner.forbidden_prefixes) == 0:
            print("\tNone")
        else:
            for text in self.scanner.forbidden_prefixes:
                print(f"\t{text}")

        print(f"Forbidden suffixes:")
        if len(self.scanner.forbidden_suffixes) == 0:
            print("\tNone")
        else:
            for text in self.scanner.forbidden_suffixes:
                print(f"\t{text}")

        print(f"Target folders:")
        if len(self.target_folders) == 0:
            print("\tNone")
        else:
            for folder in self.target_folders:
                print(f"\t{folder.resolve()}")

        print(f"Target files:")
        if len(self.targets) == 0:
            print("\tNone")
        else:
            for file in self.targets:
                print(f"\t{file.resolve()}")

        print(f"Target conversions:")
        self.converter.print_conversions()

        print()

    def menu(self) -> None:
        self.print_status()
        self.print_menu()

        try:
            option = int(input("> "))
        except ValueError:
            option = None

        if option not in self.menu_items.keys():
            return

        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        self.menu_items[option][1]()

    def run(self) -> int:
        self.running = True

        while self.running:
            self.menu()

        return 0

    def stop(self) -> None:
        self.running = False


def delete_file(file: Path) -> None:
    file.unlink()


def main():
    app = App()
    return app.run()


if __name__ == "__main__":
    main()
