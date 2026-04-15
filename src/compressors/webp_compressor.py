from shlex import quote

from ..compressor import Compressor
from ..result_item import ResultItem


class WEBPCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "webp"

    def build_command(self, result_item: ResultItem) -> str:
        command = f"cwebp {quote(result_item.filename)}"

        # cwebp doesn't preserve any metadata by default
        if self.settings.metadata:
            command += " -metadata all"

        if self.settings.lossy:
            quality = self.settings.webp_lossy_level
        else:
            command += " -lossless"
            quality = 100  # maximum cpu power for lossless

        # multithreaded, (lossless) compression mode, quality, output
        command += f" -mt -m {self.settings.webp_lossless_level}"
        command += f" -q {quality}"
        command += f" -o {quote(result_item.tmp_filename)}"

        return command
