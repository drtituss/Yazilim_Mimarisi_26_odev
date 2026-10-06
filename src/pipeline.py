from typing import Generic, TypeVar, List, Callable
from interfaces import Source, Sink, Stage, Emitter, StageException

T = TypeVar('T')

class _CallbackEmitter(Emitter[T]):
    """Bir sonraki aşamaya geçiş fonksiyonunu sarmalayan yardımcı Emitter."""
    def __init__(self, callback: Callable[[T], None]):
        self.callback = callback

    def emit(self, item: T) -> None:
        self.callback(item)

class Pipeline(Generic[T]):
    """Aşamaları sıralı tutan ve veriyi kaynaktan hedefe ileten motor."""
    def __init__(self, source: Source[T], sink: Sink[T]):
        self.source = source
        self.sink = sink
        self.stages: List[Stage[T, T]] = []

    def add_stage(self, stage: Stage[T, T]) -> 'Pipeline[T]':
        self.stages.append(stage)
        return self

    def run(self) -> None:
        # 1. Yaşam döngüsü: Varsa tüm aşamaların open() metodunu tetikle
        for stage in self.stages:
            stage.open()

        # 2. Kaynaktan üretimi başlat ve ilk aşamaya ver
        emitter = _CallbackEmitter(lambda item: self._dispatch(item, 0))
        self.source.produce(emitter)

        # 3. Yaşam döngüsü: Akış bittiğinde close() metodlarını tetikle
        for stage in self.stages:
            stage.close()

    def _dispatch(self, current_item: T, stage_index: int) -> None:
        # Eğer tüm aşamalar tamamlandıysa veriyi doğrudan Sink tüketir
        if stage_index >= len(self.stages):
            self.sink.consume(current_item)
            return

        current_stage = self.stages[stage_index]
        try:
            next_emitter = _CallbackEmitter(lambda next_item: self._dispatch(next_item, stage_index + 1))
            current_stage.process(current_item, next_emitter)
        except StageException as e:
            print(f"Pipeline işlem hatası: {e}")