from ..compressor import Compressor


class JPEGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "jpeg"

    def build_command(self, result_item) -> list[tuple[list[str], str | None]]:
        jpegoptim = ["jpegoptim", "-o", "--stdout"]

        if self.settings.lossy:  # lossy compression
            jpegoptim += ["--max", str(self.settings.jpg_lossy_level)]

        if self.settings.jpg_progressive:
            jpegoptim.append("--all-progressive")

        if not self.settings.metadata:
            jpegoptim += ["--strip-all", "--keep-icc"]

        if self.settings.file_attributes:
            jpegoptim += ["--preserve", "--preserve-perms"]

        jpegoptim.append(result_item.filename)

        return [(jpegoptim, result_item.tmp_filename)]
