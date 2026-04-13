from shlex import quote

from ..compressor import Compressor


class PNGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "png"

    def build_command(self, result_item) -> str:
        pngquant = "pngquant --quality=0-{} -f {} --output {}"
        oxipng = "oxipng -o {} -i 1 {} --out {}"

        if not self.settings.metadata:
            pngquant += " --strip"
            oxipng += " --strip safe"

        if self.settings.file_attributes:
            oxipng += " --preserve"

        if self.settings.lossy:  # lossy compression
            command = pngquant.format(
                self.settings.png_lossy_level,
                quote(result_item.filename),
                quote(result_item.tmp_filename),
            )
            command += " && "
            command += oxipng.format(
                self.settings.png_lossless_level,
                quote(result_item.tmp_filename),
                quote(result_item.tmp_filename),
            )
        else:  # lossless compression
            command = oxipng.format(
                self.settings.png_lossless_level,
                quote(result_item.filename),
                quote(result_item.tmp_filename),
            )
        return command
