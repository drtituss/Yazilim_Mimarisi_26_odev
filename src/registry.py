from typing import Callable, Dict, Any
from interfaces import Stage, Source, Sink, ConfigurationError, ErrorPolicy
from stages import FileLineSource, ConsoleSink, FileSink, DeadLetterFileSink
from parser import ParserStage
from filters import PredicateFilterStage, ProjectionStage
from validation import ValidationStage

class StageRegistry:
    """Aşama, kaynak ve hedef bileşenlerinin veri odaklı kayıt defteri."""
    _stages: Dict[str, Callable[[Dict[str, Any]], Stage]] = {}
    _sources: Dict[str, Callable[[Dict[str, Any]], Source]] = {}
    _sinks: Dict[str, Callable[[Dict[str, Any]], Sink]] = {}

    @classmethod
    def register_stage(cls, name: str, factory: Callable[[Dict[str, Any]], Stage]) -> None:
        cls._stages[name] = factory

    @classmethod
    def register_source(cls, name: str, factory: Callable[[Dict[str, Any]], Source]) -> None:
        cls._sources[name] = factory

    @classmethod
    def register_sink(cls, name: str, factory: Callable[[Dict[str, Any]], Sink]) -> None:
        cls._sinks[name] = factory

    @classmethod
    def create_stage(cls, name: str, params: Dict[str, Any]) -> Stage:
        if name not in cls._stages:
            raise ConfigurationError(f"Bilinmeyen aşama türü: '{name}'. Desteklenen: {list(cls._stages.keys())}")
        return cls._stages[name](params)

    @classmethod
    def create_source(cls, name: str, params: Dict[str, Any]) -> Source:
        if name not in cls._sources:
            raise ConfigurationError(f"Bilinmeyen kaynak türü: '{name}'. Desteklenen: {list(cls._sources.keys())}")
        return cls._sources[name](params)

    @classmethod
    def create_sink(cls, name: str, params: Dict[str, Any]) -> Sink:
        if name not in cls._sinks:
            raise ConfigurationError(f"Bilinmeyen hedef türü: '{name}'. Desteklenen: {list(cls._sinks.keys())}")
        return cls._sinks[name](params)


# --- Fabrika Fonksiyonları ---

def _get_policy(params: Dict[str, Any]) -> ErrorPolicy:
    """YAML'dan gelen error_policy değerini okur (varsayılan: FAIL_FAST)."""
    policy_str = params.get("error_policy", "FAIL_FAST").upper()
    try:
        return ErrorPolicy[policy_str]
    except KeyError:
        raise ConfigurationError(f"Geçersiz hata politikası: '{policy_str}'")

def _create_file_source(params: Dict[str, Any]) -> Source:
    if "path" not in params: raise ConfigurationError("Kaynak için 'path' eksik.")
    return FileLineSource(params["path"])

def _create_file_sink(params: Dict[str, Any]) -> Sink:
    if "path" not in params: raise ConfigurationError("Hedef için 'path' eksik.")
    return FileSink(params["path"])

def _create_console_sink(params: Dict[str, Any]) -> Sink:
    return ConsoleSink()

def _create_dead_letter_sink(params: Dict[str, Any]) -> Sink:
    if "path" not in params: raise ConfigurationError("Dead-letter hedefi için 'path' eksik.")
    return DeadLetterFileSink(params["path"])

def _create_parser_stage(params: Dict[str, Any]) -> Stage:
    fmt = params.get("format", "clf")
    if fmt != "clf": raise ConfigurationError("Yalnızca 'clf' formatı desteklenir.")
    return ParserStage(error_policy=_get_policy(params))

def _create_validation_stage(params: Dict[str, Any]) -> Stage:
    rules = params.get("rules", {})
    if not isinstance(rules, dict):
        raise ConfigurationError("Validation 'rules' bir sözlük olmalıdır.")
    return ValidationStage(rules=rules, error_policy=_get_policy(params))

def _create_filter_stage(params: Dict[str, Any]) -> Stage:
    return PredicateFilterStage.from_config(params["field"], params["op"], params["value"])

def _create_projection_stage(params: Dict[str, Any]) -> Stage:
    return ProjectionStage(params["fields"])

# Kayıtlar
StageRegistry.register_source("file", _create_file_source)
StageRegistry.register_sink("file", _create_file_sink)
StageRegistry.register_sink("console", _create_console_sink)
StageRegistry.register_sink("dead_letter_file", _create_dead_letter_sink) # YENİ HEDEF TÜRÜ

StageRegistry.register_stage("parse", _create_parser_stage)
StageRegistry.register_stage("validate", _create_validation_stage) # YENİ DOĞRULAMA AŞAMASI
StageRegistry.register_stage("filter", _create_filter_stage)
StageRegistry.register_stage("project", _create_projection_stage)