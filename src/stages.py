from typing import Any, Optional
from interfaces import Source, Sink, Emitter, StageException

class FileLineSource(Source[str]):
    """Dosyayı satır satır okuyup boru hattına aktaran kaynak bileşen."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def produce(self, out: Emitter[str]) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line in file:
                    out.emit(line.rstrip("\r\n"))
        except IOError as e:
            raise StageException(f"Dosya okuma hatası ({self.file_path}): {e}")


class ConsoleSink(Sink[Any]):
    """Gelen veriyi konsola yazdıran hedef bileşen."""

    def consume(self, item: Any) -> None:
        print(item)


class FileSink(Sink[Any]):
    """
    Çıktıyı hedef dosyaya yazan bileşen.
    open() ve close() yaşam döngüsü kancaları sayesinde kaynak sızıntısını ve
    arabellek kaybını (buffer loss) önler.
    """

    def __init__(self, output_path: str):
        self.output_path = output_path
        self._file: Optional[Any] = None

    def open(self) -> None:
        try:
            self._file = open(self.output_path, "w", encoding="utf-8")
        except IOError as e:
            raise StageException(f"Çıktı dosyası açılamadı ({self.output_path}): {e}")

    def consume(self, item: Any) -> None:
        if self._file is None:
            raise StageException("FileSink açık değil! open() çağrılmadı.")
        self._file.write(f"{item}\n")

    def close(self) -> None:
        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None