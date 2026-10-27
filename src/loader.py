import os
import yaml
from typing import Dict, Any
from interfaces import ConfigurationError
from pipeline import Pipeline, PipelineBuilder
from registry import StageRegistry

class PipelineLoader:
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
            raise ConfigurationError("Yapılandırma dosyası geçerli bir sözlük içermelidir.")
        return cls.load_from_dict(data)

    @classmethod
    def load_from_dict(cls, config: Dict[str, Any]) -> Pipeline:
        if "pipeline" not in config: raise ConfigurationError("Kök anahtar 'pipeline' olmalıdır.")
        p_cfg = config["pipeline"]
        
        # 1. Kaynak Oluşturma
        if "source" not in p_cfg: raise ConfigurationError("'source' tanımı eksik.")
        src_params = p_cfg["source"].get("params", {}) or {}
        source = StageRegistry.create_source(p_cfg["source"]["type"], src_params)
        
        builder = PipelineBuilder.from_source(source)

        # 2. Dead-Letter Kanalı (Opsiyonel İkincil Çıktı Yolu)
        if "dead_letter_sink" in p_cfg:
            dlc_cfg = p_cfg["dead_letter_sink"]
            dlc_params = dlc_cfg.get("params", {}) or {}
            dlc_sink = StageRegistry.create_sink(dlc_cfg["type"], dlc_params)
            builder.with_dead_letter(dlc_sink)

        # 3. Aşamaları Ekleme
        stages_cfg = p_cfg.get("stages", [])
        if not isinstance(stages_cfg, list) or len(stages_cfg) == 0:
            raise ConfigurationError("Boru hattı en az bir aşama (stage) içermelidir.")

        for idx, stage_cfg in enumerate(stages_cfg):
            stg_params = stage_cfg.get("params", {}) or {}
            stage_instance = StageRegistry.create_stage(stage_cfg["type"], stg_params)
            builder.via(stage_instance)

        # 4. Hedef (Sink) Oluşturma
        if "sink" not in p_cfg: raise ConfigurationError("'sink' tanımı eksik.")
        sink_params = p_cfg["sink"].get("params", {}) or {}
        sink = StageRegistry.create_sink(p_cfg["sink"]["type"], sink_params)

        return builder.to(sink)