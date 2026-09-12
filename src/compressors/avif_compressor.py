from ..compressor import Compressor
from ..result_item import ResultItem


class AVIFCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "avif"

    def _intermediate_path(self, result_item: ResultItem) -> str:
        return result_item.tmp_filename + ".png"

    def build_command(
        self, result_item: ResultItem
    ) -> list[tuple[list[str], str | None]]:
        intermediate = self._intermediate_path(result_item)

        # avifenc can't read AVIF input, so decode to a temporary PNG first
        avifdec = ["avifdec", result_item.filename, intermediate]

        avifenc = ["avifenc"]

        # avifenc preserves metadata by default
        if not self.settings.metadata:
            avifenc += ["--ignore-exif", "--ignore-xmp", "--ignore-profile"]

        if self.settings.lossy:
            avifenc += ["-q", str(self.settings.avif_lossy_level)]
        else:
            avifenc.append("--lossless")

        # higher effort -> slower but better compression (speed 0-10, default 6)
        avifenc += ["--speed", str(10 - self.settings.avif_lossless_level)]
        avifenc += [intermediate, result_item.tmp_filename]

        return [(avifdec, None), (avifenc, None)]

    def get_intermediate_files(self, result_item: ResultItem) -> list[str]:
        return [self._intermediate_path(result_item)]
