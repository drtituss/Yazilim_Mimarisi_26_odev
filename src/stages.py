import sys
from interfaces import Source, Sink
from record import FailedRecord

class FileLineSource(Source[str]):
    """Dosyadan satır satır okuyan kaynak bileşeni."""
    def __init__(self, path: str):
        self.path = path
        self.file = None

    def open(self) -> None:
        # errors="replace" EKLENDİ: UTF-8 olmayan bozuk baytlar çökertmek yerine replace edilir
        self.file = open(self.path, "r", encoding="utf-8", errors="replace")

    def close(self) -> None:
        if self.file:
            self.file.close()

    def produce(self, out) -> None:
        if self.file:
            for line in self.file:
                out.emit(line.strip())

class ConsoleSink(Sink[str]):
    """Veriyi konsola yazdıran hedef bileşen."""
    def consume(self, item: str) -> None:
        print(item)

class FileSink(Sink[str]):
    """Veriyi dosyaya yazdıran hedef bileşen."""
    def __init__(self, path: str):
        self.path = path
        self.file = None

    def open(self) -> None:
        self.file = open(self.path, "w", encoding="utf-8")

    def close(self) -> None:
        if self.file:
            self.file.close()

    def consume(self, item: str) -> None:
        if self.file:
            self.file.write(str(item) + "\n")

class DeadLetterFileSink(Sink[FailedRecord]):
    """
    Hatalı kayıtları (FailedRecord) ikincil bir hedefe (dosyaya) yazan Dead-Letter Kanalı (DLC) bileşeni.
    """
    def __init__(self, path: str):
        self.path = path
        self.file = None

    def open(self) -> None:
        self.file = open(self.path, "w", encoding="utf-8")
        self.file.write("--- DEAD LETTER CHANNEL LOGS ---\n")

    def close(self) -> None:
        if self.file:
            self.file.close()

    def consume(self, item: FailedRecord) -> None:
        if self.file:
            self.file.write(item.to_csv_line() + "\n")