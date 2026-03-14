import os
import threading
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib

from .tools import get_file_type


class CompressionManager:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.compressors = {}

    def register_compressor(self, ConcreteCompressor):
        mime_type = ConcreteCompressor.get_file_type()
        if mime_type not in self.compressors:
            self.compressors[mime_type] = ConcreteCompressor(self.settings)

    def compress(self, result_items, c_update_result_item, c_enable_compression):
        threading.Thread(
            target=self._compress,
            args=(result_items, c_update_result_item, c_enable_compression),
            daemon=True,
        ).start()

    def _compress(self, result_items, c_update_result_item, c_enable_compression):
        cpu_count = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=cpu_count)
        futures = []
        for result_item in result_items:
            file_type = get_file_type(result_item.file)
            if file_type in ("svg", "webp"):
                # Must be manually skipped
                if not self.do_new_file:
                    self.create_tmp_result_item(result_item)
            future = executor.submit(
                self.compressors[file_type].run, result_item, c_update_result_item
            )
            futures.append(future)

        for future in futures:
            future.result()
        GLib.idle_add(c_enable_compression, True)
