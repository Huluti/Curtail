from shlex import quote

from ..compressor import Compressor


class SVGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "svg"

    def build_command(self, result_item) -> str:
        command = f"scour -i {quote(result_item.filename)} -o {quote(result_item.tmp_filename)}"

        if self.settings.svg_maximum_level:
            command += " --enable-viewboxing --enable-id-stripping"
            command += " --enable-comment-stripping --shorten-ids --indent=none"

        return command
