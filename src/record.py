from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

@dataclass(frozen=True)
class LogRecord:
    """Ayrıştırılmış ve doğrulanmış yapısal log verisini temsil eden değişmez (immutable) veri modeli."""
    timestamp: datetime
    client_ip: str
    method: str
    path: str
    status: int
    bytes: int
    user_agent: str
    raw: str
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class FailedRecord:
    """
    Dead-Letter Kanalına (DLC) gönderilecek olan hatalı kayıt modeli.
    Kaydın ham verisini, hatanın oluştuğu aşamayı, istisna detayını ve zamanını içerir.
    """
    raw_input: Any
    stage_name: str
    exception: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_csv_line(self) -> str:
        """Hata dosyasında okunabilirliği artırmak için CSV benzeri basit bir format döner."""
        # Yeni satır karakterlerini temizleyerek tek satıra sığdır
        clean_raw = str(self.raw_input).replace('\n', '\\n').replace('\r', '')
        return f"[{self.timestamp.isoformat()}] STAGE: {self.stage_name} | ERROR: {self.exception} | RAW: {clean_raw}"