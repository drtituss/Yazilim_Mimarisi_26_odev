import os
import yaml
from typing import Dict, Any
from interfaces import ConfigurationError
from pipeline import Pipeline, PipelineBuilder
from registry import StageRegistry


class PipelineLoader:
    """
    Bildirimsel YAML yapılandırma dosyasını ayrıştıran,
    doğrulayan ve Pipeline nesnesini inşa eden yükleyici.
    """

    @classmethod
    def load_from_file(cls, config_path: str) -> Pipeline:
        if not os.path.exists(config_path):
            raise ConfigurationError(f"Yapılandırma dosyası bulunamadı: '{config_path}'")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"YAML sözdizimi hatası: {e}")

        if not isinstance(data, dict):
            raise ConfigurationError("Yapılandırma dosyası geçerli bir sözlük (YAML mapping) içermelidir.")

        return cls.load_from_dict(data)

    @classmethod
    def load_from_dict(cls, config: Dict[str, Any]) -> Pipeline:
        if "pipeline" not in config:
            raise ConfigurationError("Yapılandırma dosyasının kök anahtarı 'pipeline' olmalıdır.")

        p_cfg = config["pipeline"]
        if not isinstance(p_cfg, dict):
            raise ConfigurationError("'pipeline' alanı bir sözlük olmalıdır.")

        # 1. Kaynak Doğrulama ve Oluşturma
        if "source" not in p_cfg:
            raise ConfigurationError("Boru hattı için 'source' tanımı eksik.")
        src_cfg = p_cfg["source"]
        if not isinstance(src_cfg, dict) or "type" not in src_cfg:
            raise ConfigurationError("Kaynak tanımı 'type' alanı içermelidir.")
        src_params = src_cfg.get("params", {}) or {}
        source = StageRegistry.create_source(src_cfg["type"], src_params)

        builder = PipelineBuilder.from_source(source)

        # 2. Aşamaları Doğrulama ve Ekleme
        stages_cfg = p_cfg.get("stages", [])
        if not isinstance(stages_cfg, list):
            raise ConfigurationError("'stages' alanı bir liste olmalıdır.")
        if len(stages_cfg) == 0:
            raise ConfigurationError("Boru hattı en az bir aşama (stage) içermelidir. Boş boru hattı geçersizdir.")

        for idx, stage_cfg in enumerate(stages_cfg):
            if not isinstance(stage_cfg, dict) or "type" not in stage_cfg:
                raise ConfigurationError(f"{idx + 1}. aşama tanımı eksik veya 'type' alanı içermiyor.")
            stg_params = stage_cfg.get("params", {}) or {}
            stage_instance = StageRegistry.create_stage(stage_cfg["type"], stg_params)
            builder.via(stage_instance)

        # 3. Hedef (Sink) Doğrulama ve Oluşturma
        if "sink" not in p_cfg:
            raise ConfigurationError("Boru hattı için 'sink' tanımı eksik.")
        sink_cfg = p_cfg["sink"]
        if not isinstance(sink_cfg, dict) or "type" not in sink_cfg:
            raise ConfigurationError("Hedef tanımı 'type' alanı içermelidir.")
        sink_params = sink_cfg.get("params", {}) or {}
        sink = StageRegistry.create_sink(sink_cfg["type"], sink_params)

        return builder.to(sink)