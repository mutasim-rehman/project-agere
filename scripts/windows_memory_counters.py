"""System-wide Windows paging indicators via English PDH counter names."""
import ctypes
from ctypes import wintypes


COUNTERS = {
    "pages_input_per_second": r"\Memory\Pages Input/sec",
    "pages_output_per_second": r"\Memory\Pages Output/sec",
}


class CounterValue(ctypes.Structure):
    _fields_ = [("status", wintypes.DWORD), ("value", ctypes.c_double)]


class MemoryCounters:
    def __enter__(self):
        self.pdh = ctypes.WinDLL("pdh")
        handle = wintypes.HANDLE
        pointer = ctypes.POINTER
        self.pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_size_t, pointer(handle)]
        self.pdh.PdhAddEnglishCounterW.argtypes = [handle, wintypes.LPCWSTR, ctypes.c_size_t, pointer(handle)]
        self.pdh.PdhCollectQueryData.argtypes = [handle]
        self.pdh.PdhGetFormattedCounterValue.argtypes = [
            handle, wintypes.DWORD, pointer(wintypes.DWORD), pointer(CounterValue)]
        self.pdh.PdhCloseQuery.argtypes = [handle]
        self.query = handle()
        self.check(self.pdh.PdhOpenQueryW(None, 0, ctypes.byref(self.query)))
        self.counters = {}
        try:
            for name, path in COUNTERS.items():
                counter = handle()
                self.check(self.pdh.PdhAddEnglishCounterW(self.query, path, 0, ctypes.byref(counter)))
                self.counters[name] = counter
            self.check(self.pdh.PdhCollectQueryData(self.query))
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    @staticmethod
    def check(status):
        if status:
            raise OSError(f"Windows PDH status 0x{status & 0xffffffff:08x}")

    def sample(self):
        self.check(self.pdh.PdhCollectQueryData(self.query))
        result = {}
        for name, counter in self.counters.items():
            value = CounterValue()
            self.check(self.pdh.PdhGetFormattedCounterValue(counter, 0x200, None, ctypes.byref(value)))
            if value.status not in (0, 1):
                raise OSError(f"Windows PDH counter {name} status 0x{value.status:08x}")
            result[name] = value.value
        return result

    def __exit__(self, *_):
        self.pdh.PdhCloseQuery(self.query)
