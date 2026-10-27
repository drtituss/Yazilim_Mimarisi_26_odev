import re
from datetime import datetime
from typing import Dict, Any
from interfaces import Stage, Emitter, StageException, ErrorPolicy
from record import LogRecord

class ValidationStage(Stage[LogRecord, LogRecord]):
    """
    Kayıtları bildirimsel kurallara (YAML'dan gelen) göre doğrulayan aşama.
    Kurallara uymayan kayıtlar için StageException fırlatılır.
    """

    IP_PATTERN = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    def __init__(self, rules: Dict[str, Any], error_policy: ErrorPolicy = ErrorPolicy.DEAD_LETTER):
        super().__init__(error_policy)
        self.rules = rules

    def process(self, input_item: LogRecord, out: Emitter[LogRecord]) -> None:
        # 1. Zorunlu Alan Kontrolü
        required_fields = self.rules.get("required_fields", [])
        for field in required_fields:
            if not hasattr(input_item, field) and field not in input_item.attributes:
                raise StageException(f"Zorunlu alan eksik: '{field}'")

        # 2. Sayısal Aralık Kontrolü (Örn: Negatif bayt sayıları)
        numeric_ranges = self.rules.get("numeric_ranges", {})
        for field, ranges in numeric_ranges.items():
            val = getattr(input_item, field, None)
            if val is not None:
                min_val = ranges.get("min", float('-inf'))
                max_val = ranges.get("max", float('inf'))
                if not (min_val <= val <= max_val):
                    raise StageException(f"Değer sınırların dışında: '{field}'={val} (Beklenen: {min_val}-{max_val})")

        # 3. IP Biçimi Doğrulaması
        if self.rules.get("check_ip_format", False):
            if not self.IP_PATTERN.match(input_item.client_ip):
                raise StageException(f"Geçersiz IP adresi biçimi: '{input_item.client_ip}'")

        # 4. Zaman Damgası Tutarlılığı (Örn: 1970 ve 2099 hatalarını yakala)
        timestamp_rules = self.rules.get("timestamp_rules", {})
        if timestamp_rules:
            min_year = timestamp_rules.get("min_year", 1990)
            max_year = timestamp_rules.get("max_year", datetime.now().year + 1)
            if input_item.timestamp.year < min_year or input_item.timestamp.year > max_year:
                raise StageException(f"Mantıksız zaman damgası yılı: {input_item.timestamp.year}")

        # Kuralları geçen kayıt ana akışa (bir sonraki aşamaya) iletilir
        out.emit(input_item)