from ..compressor import Compressor
from ..result_item import ResultItem


class WEBPCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "webp"

    def build_command(self, result_item: ResultItem) -> list[tuple[list[str], str | None]]:
        cwebp = []

        # cwebp doesn't preserve any metadata by default
        if self.settings.metadata:
            cwebp += ["-metadata", "all"]

        if self.settings.lossy:
            quality = self.settings.webp_lossy_level
        else:
            cwebp.append("-lossless")
            quality = 100  # maximum cpu power for lossless

        # multithreaded, (lossless) compression mode, quality, output
        cwebp += [
            "-mt",
            "-m",
            str(self.settings.webp_lossless_level),
            "-q",
            str(quality),
            "-o",
            result_item.tmp_filename,
        ]
        cwebp.append(result_item.filename)

        return [(cwebp, None)]