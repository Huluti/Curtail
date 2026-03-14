from shlex import quote

from ..compressor import Compressor


class SVGCompressor(Compressor):
    @classmethod
    def get_file_type(cls) -> str:
        return "svg"

    def build_command(self, result_item):
        # workaround for https://github.com/scour-project/scour/issues/129
        temp_new_filename = result_item.new_filename
        if not self.settings.new_file:
            temp_new_filename = "{}.temp".format(result_item.new_filename)

        command = "scour -i {} -o {}".format(
            quote(result_item.filename), quote(temp_new_filename)
        )

        if self.settings.svg_maximum_level:
            command += " --enable-viewboxing --enable-id-stripping"
            command += " --enable-comment-stripping --shorten-ids --indent=none"

        if not self.settings.new_file:
            command += " && mv {} {}".format(
                quote(temp_new_filename), quote(result_item.new_filename)
            )

        return command
