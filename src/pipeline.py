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
        # 1. Yaşam döngüsü: Varsa open() metodlarını güvenle tetikle
        if hasattr(self.source, 'open'):
            self.source.open()
        for stage in self.stages:
            if hasattr(stage, 'open'):
                stage.open()
        if hasattr(self.sink, 'open'):
            self.sink.open()

        try:
            # 2. Kaynaktan üretimi başlat ve ilk aşamaya yönlendir
            emitter = _CallbackEmitter(lambda item: self._dispatch(item, 0))
            self.source.produce(emitter)
        finally:
            # 3. Yaşam döngüsü: Varsa close() metodlarını güvenle tetikle
            for stage in self.stages:
                if hasattr(stage, 'close'):
                    stage.close()
            if hasattr(self.sink, 'close'):
                self.sink.close()
            if hasattr(self.source, 'close'):
                self.source.close()

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


class PipelineBuilder:
    """
    Akıcı (Fluent) Pipeline kurucu sınıfı.
    Pipeline bileşenlerinin zincirleme metotlarla kurulmasını sağlar.
    """
    def __init__(self, source: Source[Any]):
        self._source = source
        self._stages: List[Stage[Any, Any]] = []

    @classmethod
    def from_source(cls, source: Source[Any]) -> 'PipelineBuilder':
        return cls(source)

    def via(self, stage: Stage[Any, Any]) -> 'PipelineBuilder':
        self._stages.append(stage)
        return self

    def to(self, sink: Sink[Any]) -> Pipeline:
        pipeline = Pipeline(self._source, sink)
        for stage in self._stages:
            pipeline.add_stage(stage)
        return pipeline