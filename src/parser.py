import re
from datetime import datetime
from typing import Any
from interfaces import Stage, Emitter, StageException, ErrorPolicy
from record import LogRecord

class ParserStage(Stage[Any, LogRecord]):
    """Common Log Format (CLF) ayrıştırıcısı. Hatalı satırlarda StageException fırlatır."""
    
    LOG_PATTERN = re.compile(
        r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d+)\s+(?P<bytes>-|\d+)\s+"(?P<user_agent>[^"]*)"$'
    )

    def __init__(self, error_policy: ErrorPolicy = ErrorPolicy.DEAD_LETTER):
        # Varsayılan politika olarak hatalı kayıtları Dead-Letter kanalına gönder
        super().__init__(error_policy)

    def process(self, input_item: Any, out: Emitter[LogRecord]) -> None:
        line = str(input_item).strip()
        
        if not line:
            raise StageException("Satır tamamen boş.")

        match = self.LOG_PATTERN.match(line)
        if not match:
            # ÖNCEKİ GİBİ SESSİZCE ATLAMAYIP HATA FIRLATIYORUZ (Fail Fast veya Dead-Letter için)
            raise StageException("CLF (Common Log Format) regex eşleşmedi veya bozuk satır.")

        try:
            data = match.groupdict()
            ts_str = data["timestamp"].split(" ")[0]
            ts = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S")
            status = int(data["status"])
            bytes_val = 0 if data["bytes"] == "-" else int(data["bytes"])

            record = LogRecord(
                timestamp=ts,
                client_ip=data["ip"],
                method=data["method"],
                path=data["path"],
                status=status,
                bytes=bytes_val,
                user_agent=data["user_agent"],
                raw=line
            )
            out.emit(record)
        except Exception as e:
            raise StageException(f"Veri dönüşüm hatası (Tarih/Sayı): {e}")