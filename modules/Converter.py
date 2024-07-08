from multiprocessing.pool import ThreadPool
from typing import Tuple
from pathlib import Path
import ffmpeg

# FORMAT_MAP = {
#     ".mp4": ".webm",
#     ".mov": ".webm",
#     ".mkv": ".webm",
#     ".png": ".webp",
#     ".jpg": ".webp",
#     ".jpeg": ".webp",
# }


class Converter:
    def __init__(self):
        self.format_associations: map[str, list[str]] = {}
        self.conversions: list[Path, Path] = []
        self.threads = 2

    def convert(self, pair: Tuple[Path, Path]):
        if self.pair_exists(pair):
            print("Pair already exists -- ", end="")
            self.print_pair(pair)
            return

        print(f"Processing {pair[1]}...")

        stream = ffmpeg.input(str(pair[0]))
        stream = ffmpeg.output(stream, str(pair[1]), loglevel="error")
        ffmpeg.run(stream)

    def pair_exists(self, pair: Tuple[Path, Path]):
        return pair[0].exists() and pair[1].exists()

    def resolve_file(self, path: Path) -> None:
        for key in self.format_associations.keys():
            if path.suffix == key:
                for suf in self.format_associations[key]:
                    pair = (path, path.with_suffix(suf))
                    if pair not in self.conversions:
                        self.conversions.append(pair)

    def print_conversions(self) -> None:
        for i, conversion in enumerate(self.conversions):
            print(f"""{i+1}:\t\"{conversion[0]}\" → \"{conversion[1]}\"""")

    def remove_conversions(self, indexes: list[int]) -> None:
        indexes = \
            sorted(
                filter(
                    lambda x: x >= 0 and x < len(self.conversions),
                    list(set(indexes))
                )
            )[::-1]

        for index in indexes:
            self.conversions.pop(index)

    def convert_all(self) -> int:
        rc = 0

        with ThreadPool(processes=self.threads) as pool:
            # try:
            pool.map(self.convert, self.conversions)
            # except:
            #     rc += 1

        self.conversions = []

        return rc

    def add_conversion(self, src: str, dst: str) -> None:
        if src not in self.format_associations.keys():
            self.format_associations[src] = []

        self.format_associations[src].append(dst)
