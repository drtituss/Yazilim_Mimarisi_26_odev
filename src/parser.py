import re
from datetime import datetime
from interfaces import Stage, Emitter, StageException
from record import LogRecord

class ParserStage(Stage[str, LogRecord]):
    """Ham log satırlarını ayrıştırıp LogRecord nesnelerine dönüştüren aşama."""

    # Common Log Format (CLF) + opsiyonel User Agent deseni
    CLF_REGEX = re.compile(
        r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"([A-Z]+)\s+(\S+)\s+HTTP/[^"]+"\s+(\d{3})\s+(\d+|-)(?:\s+"([^"]*)")?'
    )

    def __init__(self):
        self.error_count = 0

    def process(self, input_item: str, out: Emitter[LogRecord]) -> None:
        line = input_item.strip()
        if not line:
            self.error_count += 1
            return

        match = self.CLF_REGEX.match(line)
        if not match:
            self.error_count += 1
            return

        client_ip, raw_time, method, path, raw_status, raw_bytes, user_agent = match.groups()

        try:
            timestamp = datetime.strptime(raw_time, "%d/%b/%Y:%H:%M:%S %z")
            status = int(raw_status)
            bytes_sent = 0 if raw_bytes == "-" else int(raw_bytes)
            ua = user_agent if user_agent else "-"

            record = LogRecord(
                timestamp=timestamp,
                client_ip=client_ip,
                method=method,
                path=path,
                status=status,
                bytes=bytes_sent,
                user_agent=ua,
                raw=input_item
            )
            out.emit(record)

        except (ValueError, Exception):
            self.error_count += 1

    def close(self) -> None:
        print(f"\n[Parser] İşlem tamamlandı. Toplam atlanan/hatalı satır sayısı: {self.error_count}")