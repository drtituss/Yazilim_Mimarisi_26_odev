from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from enum import Enum

I = TypeVar('I')
O = TypeVar('O')
T = TypeVar('T')

class ConfigurationError(Exception):
    """Yapılandırma dosyasındaki sözdizimi, eksik alan, geçersiz aşama veya tip hatalarında fırlatılır."""
    pass

class StageException(Exception):
    """
    Bir aşamada tek bir kayıt işlenirken hata oluştuğunda fırlatılır (Kurtarılabilir hata).
    """
    pass

class PipelineException(Exception):
    """
    İşlem hattı devam edemez duruma geldiğinde fırlatılır (Kurtarılamaz hata).
    Örnek: Okunamayan dosya, diskin dolması, yetki hatası.
    """
    pass

class ErrorPolicy(Enum):
    """Aşama bazında uygulanabilecek hata yönetim politikaları."""
    FAIL_FAST = "FAIL_FAST"         # Çalıştırmayı anında durdur ve çöktür.
    SKIP = "SKIP"                   # Hatalı kaydı atla, sayısını tut, akışa devam et.
    DEAD_LETTER = "DEAD_LETTER"     # Hatalı kaydı ikincil bir hedefe (Dead-Letter Channel) gönder.
    RETRY = "RETRY"                 # İşlemi tekrar dene (Gelecek haftalarda I/O için kullanılacak).

class Emitter(ABC, Generic[T]):
    """Veriyi bir sonraki aşamaya ileten arayüz."""
    @abstractmethod
    def emit(self, item: T) -> None:
        pass

class Stage(ABC, Generic[I, O]):
    """Veriyi işleyen aşama / filtre arayüzü."""
    
    def __init__(self, error_policy: ErrorPolicy = ErrorPolicy.FAIL_FAST):
        self.error_policy = error_policy

    @abstractmethod
    def process(self, input_item: I, out: Emitter[O]) -> None:
        pass

    def open(self) -> None:
        pass

    def close(self) -> None:
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