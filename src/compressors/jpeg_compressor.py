from shlex import quote

from ..compressor import Compressor


class JPEGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "jpeg"

    @classmethod
    def has_native_skip_capacity(cls) -> bool:
        return True

    def build_command(self, result_item):
        if self.settings.new_file:
            jpegoptim = "jpegoptim --max={} -o --stdout {} > {}"
            jpegoptim2 = "jpegoptim -o --stdout {} > {}"
        else:
            jpegoptim = "jpegoptim --max={} -o {}"
            jpegoptim2 = "jpegoptim -o {}"

        if self.settings.jpg_progressive:
            jpegoptim += " --all-progressive"
            jpegoptim2 += " --all-progressive"

        if not self.settings.metadata:
            jpegoptim += " --strip-all"
            jpegoptim2 += " --strip-all"

        if self.settings.file_attributes:
            jpegoptim += " --preserve --preserve-perms"
            jpegoptim2 += " --preserve --preserve-perms"

        if self.settings.lossy:  # lossy compression
            if self.settings.new_file:
                command = jpegoptim.format(
                    self.settings.jpg_lossy_level,
                    quote(result_item.filename),
                    quote(result_item.new_filename),
                )
            else:
                command = jpegoptim.format(
                    self.settings.jpg_lossy_level, quote(result_item.filename)
                )
        else:  # lossless compression
            if self.settings.new_file:
                command = jpegoptim2.format(
                    quote(result_item.filename), quote(result_item.new_filename)
                )
            else:
                command = jpegoptim2.format(quote(result_item.filename))
        return command
