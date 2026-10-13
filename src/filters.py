from typing import Callable, List, Dict, Any
from interfaces import Stage, Emitter
from record import LogRecord

class PredicateFilterStage(Stage[LogRecord, LogRecord]):
    """Bir kaydı yalnızca verilen predicate koşulunu sağlıyorsa ileten filtre aşaması."""

    def __init__(self, predicate: Callable[[LogRecord], bool]):
        self.predicate = predicate

    def process(self, input_item: LogRecord, out: Emitter[LogRecord]) -> None:
        if self.predicate(input_item):
            out.emit(input_item)


class ProjectionStage(Stage[LogRecord, Dict[str, Any]]):
    """
    Her kaydı yalnızca seçilen alanların bir alt kümesine indirger.
    Veri minimizasyonu (Data Minimization) ve çıktı boyutu/gizlilik optimizasyonu sağlar.
    """

    def __init__(self, fields: List[str]):
        self.fields = [f.strip() for f in fields]

    def process(self, input_item: LogRecord, out: Emitter[Dict[str, Any]]) -> None:
        projected = {}
        for field in self.fields:
            if hasattr(input_item, field):
                projected[field] = getattr(input_item, field)
            elif field in input_item.attributes:
                projected[field] = input_item.attributes[field]
        out.emit(projected)