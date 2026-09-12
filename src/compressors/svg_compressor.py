from ..compressor import Compressor


class SVGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "svg"

    def build_command(self, result_item) -> list[tuple[list[str], str | None]]:
        scour = ["scour", "-i", result_item.filename, "-o", result_item.tmp_filename]

        if self.settings.svg_maximum_level:
            scour += [
                "--enable-viewboxing",
                "--enable-id-stripping",
                "--enable-comment-stripping",
                "--shorten-ids",
                "--indent=none",
            ]

        return [(scour, None)]
