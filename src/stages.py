from interfaces import Source, Sink, Emitter

class FileLineSource(Source[str]):
    """Dosyayı satır satır okuyup boru hattına emit eden kaynak bileşen."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def produce(self, out: Emitter[str]) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line in file:
                    out.emit(line.rstrip("\r\n"))
        except IOError as e:
            print(f"Dosya okuma hatası: {e}")

class ConsoleSink(Sink[str]):
    """Gelen veriyi doğrudan konsola yazdıran hedef bileşen."""
    def consume(self, item: str) -> None:
        print(item)