from shlex import quote

from ..compressor import Compressor


class WEBPCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "webp"

    def build_command(self, result_item) -> str:
        command = "cwebp {}".format(quote(result_item.filename))

        # cwebp doesn't preserve any metadata by default
        if self.settings.metadata:
            command += " -metadata all"

        if self.settings.lossy:
            quality = self.settings.webp_lossy_level
        else:
            command += " -lossless"
            quality = 100  # maximum cpu power for lossless

        # multithreaded, (lossless) compression mode, quality, output
        command += " -mt -m {}".format(self.settings.webp_lossless_level)
        command += " -q {}".format(quality)
        command += " -o {}".format(quote(result_item.tmp_filename))

        return command
