from ..compressor import Compressor


class PNGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "png"

    def build_command(self, result_item) -> list[tuple[list[str], str | None]]:
        commands = []

        if self.settings.lossy:  # lossy compression
            pngquant = [
                "pngquant",
                f"--quality=0-{self.settings.png_lossy_level}",
                "-f",
            ]
            if not self.settings.metadata:
                pngquant.append("--strip")
            pngquant += [result_item.filename, "--output", result_item.tmp_filename]
            commands.append((pngquant, None))

        oxipng = ["oxipng", "-o", str(self.settings.png_lossless_level), "-i", "1"]
        if not self.settings.metadata:
            oxipng += ["--strip", "safe"]
        if self.settings.file_attributes:
            oxipng.append("--preserve")

        if self.settings.lossy:
            oxipng += [result_item.tmp_filename, "--out", result_item.tmp_filename]
        else:  # lossless compression
            oxipng += [result_item.filename, "--out", result_item.tmp_filename]

        commands.append((oxipng, None))
        return commands
