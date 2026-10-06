from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar('I')
O = TypeVar('O')
T = TypeVar('T')

class StageException(Exception):
    """Pipeline aşamalarında meydana gelen özel hata türü."""
    pass

class Emitter(ABC, Generic[T]):
    """Veriyi bir sonraki aşamaya ileten arayüz."""
    @abstractmethod
    def emit(self, item: T) -> None:
        pass

class Stage(ABC, Generic[I, O]):
    """Veriyi işleyen aşama / filtre arayüzü."""
    @abstractmethod
    def process(self, input_item: I, out: Emitter[O]) -> None:
        pass

    def open(self) -> None:
        """Yaşam döngüsü kancası (gerekli kaynakları açmak için)."""
        pass

    def close(self) -> None:
        """Yaşam döngüsü kancası (kaynakları kapatmak için)."""
        pass

class Source(ABC, Generic[O]):
    """Boru hattına veri üreten kaynak arayüzü."""
    @abstractmethod
    def produce(self, out: Emitter[O]) -> None:
        pass

class Sink(ABC, Generic[I]):
    """Boru hattından gelen veriyi tüketen hedef arayüzü."""
    @abstractmethod
    def consume(self, item: I) -> None:
        pass