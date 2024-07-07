from multiprocessing.pool import ThreadPool
import ffmpeg
import os
import sys
from typing import Tuple, Iterator


FORMAT_MAP = {
    ".mp4": ".webm",
    ".mov": ".webm",
    ".mkv": ".webm",
    ".png": ".webp",
    ".jpg": ".webp",
    ".jpeg": ".webp",
}

FORBIDDEN_PREFIXES = ["."]


def forbidden(filename: str) -> bool:
    return any(filename.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def delete_file(filename: str) -> None:
    if os.path.isfile(filename) or os.path.islink(filename):
        os.unlink(filename)


def get_subdirs(dir_path: str) -> list[str]:
    # for filename in os.listdir(dir_path):
    #     print(os.path.join(dir_path, filename),
    #           os.path.isdir(os.path.join(dir_path, filename)), forbidden(filename))
    try:
        return sorted(
            list(
                filter(
                    lambda name: os.path.isdir(
                        os.path.join(dir_path, name)) and not forbidden(name),
                    map(
                        lambda filename: os.fsdecode(filename),
                        os.listdir(os.fsencode(dir_path))
                    )
                )
            )
        )
    except:
        return []


def convert(pair: Tuple[str, str]):
    stream = ffmpeg.input(pair[0])
    stream = ffmpeg.output(stream, pair[1])
    ffmpeg.run(stream)


def pair_exists(pair: Tuple[str, str]):
    return os.path.exists(pair[0]) and os.path.exists(pair[1])


def check_files(path: str) -> list[Tuple[str, str]]:
    res: list[Tuple[str, str]] = []

    try:
        for filename in os.listdir(path):
            for key in FORMAT_MAP.keys():
                if filename.endswith(key) and not forbidden(filename):
                    filepath = os.path.abspath(os.path.join(path, filename))
                    pair = \
                        (filepath, filepath.removesuffix(
                            key) + FORMAT_MAP[key])
                    if not pair_exists(pair):
                        res.append(pair)
    except:
        ...

    return res


def get_conversions(path: str) -> list[Tuple[str, str]]:
    print("Checking", path)

    res: list[Tuple[str, str]] = check_files(path)

    subdirs = get_subdirs(path)
    for subdir in subdirs:
        res += get_conversions(os.path.join(path, subdir))

    return res


def get_path() -> Iterator[str]:
    args = sys.argv

    if len(args) == 1:
        yield "./"
        return "fin"

    for arg in args[1:]:
        yield arg
    return "fin"


def print_conversions(conversions: list[Tuple[str, str]]):
    for conversion in conversions:
        print(f"""\"{conversion[0]}\" → \"{conversion[1]}\"""")


def unique(arr: list) -> list:
    return [x for i, x in enumerate(arr) if i == arr.index(x)]


def convert_all(conversions: list[Tuple[str, str]], processes: int = 2):
    errors = 0
    with ThreadPool(processes=processes) as pool:
        try:
            pool.map(convert, conversions)
        except:
            errors += 1

    print(f"{errors=}")


def remove_originals(conversions: list[Tuple[str, str]]):
    errors = 0
    for conversion in conversions:
        try:
            delete_file(conversion[0])
        except:
            errors += 1

    print(f"{errors=}")


def main():
    conversions = []
    for path in get_path():
        conversions += get_conversions(path)
        print()

    conversions = unique(conversions)
    print_conversions(conversions)

    conf1 = input(
        "Do you want to convert the files?\n" +
        "Type YES in caps, to proceed\n" +
        "> ")

    if conf1 != "YES":
        print("A wise decision, have a great day")
        return 0

    conf2 = input(
        "Do you want to remove the original files afterwards?\n" +
        "Type YES in caps if you want to (this feature was not tested, make a backup just in case)\n" +
        "> ")

    print("This may take a very long time\n100 1 minute files from mp4 to webm took 7 hrs for me\nBe patient...")
    procs = input(
        "How many processes would you like to run in parallel? default = 2\n>")

    try:
        procs = int(procs)
    except:
        procs = 2

    if procs < 1:
        procs = 1

    convert_all(conversions, processes=procs)

    if conf2 == "YES":
        remove_originals(conversions)

    return 0


if __name__ == "__main__":
    main()
