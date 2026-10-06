from typing import Any, List, Callable
from interfaces import Source, Sink, Stage, Emitter, StageException

class _CallbackEmitter(Emitter[Any]):
    """Bir sonraki aşamaya geçiş fonksiyonunu sarmalayan yardımcı Emitter."""
    def __init__(self, callback: Callable[[Any], None]):
        self.callback = callback

    def emit(self, item: Any) -> None:
        self.callback(item)

class Pipeline:
    """Aşamaları sıralı tutan ve veriyi kaynaktan hedefe ileten motor."""
    def __init__(self, source: Source[Any], sink: Sink[Any]):
        self.source = source
        self.sink = sink
        self.stages: List[Stage[Any, Any]] = []

    def add_stage(self, stage: Stage[Any, Any]) -> 'Pipeline':
        self.stages.append(stage)
        return self

    def run(self) -> None:
        # 1. Yaşam döngüsü: Varsa tüm aşamaların open() metodunu tetikle
        for stage in self.stages:
            stage.open()

        # 2. Kaynaktan üretimi başlat ve ilk aşamaya yönlendir
        emitter = _CallbackEmitter(lambda item: self._dispatch(item, 0))
        self.source.produce(emitter)

        # 3. Yaşam döngüsü: Akış bittiğinde close() metodlarını tetikle
        for stage in self.stages:
            stage.close()

    def _dispatch(self, current_item: Any, stage_index: int) -> None:
        if stage_index >= len(self.stages):
            self.sink.consume(current_item)
            return

        current_stage = self.stages[stage_index]
        try:
            next_emitter = _CallbackEmitter(lambda next_item: self._dispatch(next_item, stage_index + 1))
            current_stage.process(current_item, next_emitter)
        except StageException as e:
            print(f"Pipeline işlem hatası: {e}")