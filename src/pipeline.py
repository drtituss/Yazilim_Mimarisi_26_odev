import time
from typing import Any, List, Callable, Dict, Optional
from interfaces import Source, Sink, Stage, Emitter, StageException, PipelineException, ErrorPolicy
from record import FailedRecord

class RunSummary:
    """Çalıştırma istatistiklerini tutan ve özetleyen sınıf."""
    def __init__(self):
        self.total_in = 0
        self.total_out = 0
        self.dropped_per_stage: Dict[str, int] = {}
        self.dead_letter_count = 0
        self.start_time = 0.0
        self.end_time = 0.0

    @property
    def elapsed_time(self) -> float:
        return self.end_time - self.start_time

    def print_summary(self):
        print("\n" + "="*45)
        print(" PIPELINE RUN SUMMARY")
        print("="*45)
        print(f" Total Incoming Records : {self.total_in}")
        print(f" Total Outgoing Records : {self.total_out}")
        print(f" Dead-Letter Records    : {self.dead_letter_count}")
        print(f" Elapsed Time           : {self.elapsed_time:.4f} seconds")
        if self.dropped_per_stage:
            print(" Dropped by Stage:")
            for stage, count in self.dropped_per_stage.items():
                if count > 0:
                    print(f"   - {stage}: {count}")
        print("="*45 + "\n")

class _CallbackEmitter(Emitter[Any]):
    def __init__(self, callback: Callable[[Any], None]):
        self.callback = callback

    def emit(self, item: Any) -> None:
        self.callback(item)

class Pipeline:
    """
    Aşamaları sıralı tutan, veriyi yöneten ve hata politikalarını 
    (SKIP, DEAD_LETTER, FAIL_FAST) uygulayan motor.
    """
    def __init__(self, source: Source[Any], sink: Sink[Any], dead_letter_sink: Optional[Sink[FailedRecord]] = None):
        self.source = source
        self.sink = sink
        self.dead_letter_sink = dead_letter_sink
        self.stages: List[Stage[Any, Any]] = []
        self.summary = RunSummary()

    def add_stage(self, stage: Stage[Any, Any]) -> 'Pipeline':
        self.stages.append(stage)
        self.summary.dropped_per_stage[stage.__class__.__name__] = 0
        return self

    def run(self) -> RunSummary:
        self.summary.start_time = time.time()
        
        # 1. Yaşam döngüsü: open() metodları
        if hasattr(self.source, 'open'): self.source.open()
        for stage in self.stages:
            if hasattr(stage, 'open'): stage.open()
        if hasattr(self.sink, 'open'): self.sink.open()
        if self.dead_letter_sink and hasattr(self.dead_letter_sink, 'open'):
            self.dead_letter_sink.open()

        try:
            # 2. Üretimi başlat ve ilk aşamaya yönlendir (total_in sayacı ile)
            def _initial_dispatch(item: Any):
                self.summary.total_in += 1
                self._dispatch(item, 0, original_raw=item)

            emitter = _CallbackEmitter(_initial_dispatch)
            self.source.produce(emitter)
            
        except Exception as e:
            # İşlem hattının devam etmesini engelleyen (PipelineException vb.) kritik hatalar
            raise PipelineException(f"Boru hattı çöktü (Kritik Hata): {e}") from e
            
        finally:
            # 3. Yaşam döngüsü: close() metodları
            for stage in self.stages:
                if hasattr(stage, 'close'): stage.close()
            if hasattr(self.sink, 'close'): self.sink.close()
            if self.dead_letter_sink and hasattr(self.dead_letter_sink, 'close'):
                self.dead_letter_sink.close()
            if hasattr(self.source, 'close'): self.source.close()

            self.summary.end_time = time.time()
            self.summary.print_summary()
            
        return self.summary

    def _dispatch(self, current_item: Any, stage_index: int, original_raw: Any = None) -> None:
        if stage_index >= len(self.stages):
            self.summary.total_out += 1
            self.sink.consume(current_item)
            return

        current_stage = self.stages[stage_index]
        stage_name = current_stage.__class__.__name__

        def _next_step(next_item: Any):
            self._dispatch(next_item, stage_index + 1, original_raw=original_raw)

        try:
            next_emitter = _CallbackEmitter(_next_step)
            current_stage.process(current_item, next_emitter)
            
        except StageException as e:
            # Hata Yalıtımı ve Topolojik Yönlendirme (Error Policy)
            policy = current_stage.error_policy
            
            if policy == ErrorPolicy.FAIL_FAST:
                raise PipelineException(f"[{stage_name}] FAIL_FAST tetiklendi. Hata: {e}") from e
                
            elif policy == ErrorPolicy.SKIP:
                self.summary.dropped_per_stage[stage_name] += 1
                
            elif policy == ErrorPolicy.DEAD_LETTER:
                if self.dead_letter_sink:
                    failed_rec = FailedRecord(
                        raw_input=original_raw if original_raw is not None else current_item,
                        stage_name=stage_name,
                        exception=str(e)
                    )
                    self.dead_letter_sink.consume(failed_rec)
                    self.summary.dead_letter_count += 1
                self.summary.dropped_per_stage[stage_name] += 1

class PipelineBuilder:
    """Akıcı (Fluent) Pipeline kurucu sınıfı (DLC desteğiyle güncellendi)."""
    def __init__(self, source: Source[Any]):
        self._source = source
        self._stages: List[Stage[Any, Any]] = []
        self._dlc_sink: Optional[Sink[FailedRecord]] = None

    @classmethod
    def from_source(cls, source: Source[Any]) -> 'PipelineBuilder':
        return cls(source)

    def via(self, stage: Stage[Any, Any]) -> 'PipelineBuilder':
        self._stages.append(stage)
        return self

    def with_dead_letter(self, sink: Sink[FailedRecord]) -> 'PipelineBuilder':
        """İkincil hata hedefini (Dead-Letter Channel) boru hattına ekler."""
        self._dlc_sink = sink
        return self

    def to(self, sink: Sink[Any]) -> Pipeline:
        pipeline = Pipeline(self._source, sink, self._dlc_sink)
        for stage in self._stages:
            pipeline.add_stage(stage)
        return pipeline