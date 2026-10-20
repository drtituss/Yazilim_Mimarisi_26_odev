import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from interfaces import ConfigurationError
from loader import PipelineLoader
from pipeline import Pipeline


class TestPipelineLoader(unittest.TestCase):

    def setUp(self):
        # Geçerli bir temel yapılandırma sözlüğü
        self.valid_config = {
            "pipeline": {
                "name": "test-pipeline",
                "source": {
                    "type": "file",
                    "params": {"path": "data/access-small.log"}
                },
                "stages": [
                    {"type": "parse", "params": {"format": "clf"}},
                    {"type": "filter", "params": {"field": "status", "op": ">=", "value": 400}},
                    {"type": "project", "params": {"fields": ["client_ip", "status"]}}
                ],
                "sink": {
                    "type": "console",
                    "params": {}
                }
            }
        }

    def test_valid_configuration(self):
        """1. Geçerli bir yapılandırma başarıyla Pipeline nesnesi üretmelidir."""
        pipeline = PipelineLoader.load_from_dict(self.valid_config)
        self.assertIsInstance(pipeline, Pipeline)
        self.assertEqual(len(pipeline.stages), 3)

    def test_unknown_stage_type(self):
        """2. Bilinmeyen bir aşama türü ConfigurationError fırlatmalıdır."""
        cfg = dict(self.valid_config)
        cfg["pipeline"] = dict(self.valid_config["pipeline"])
        cfg["pipeline"]["stages"] = [
            {"type": "non_existent_stage", "params": {}}
        ]

        with self.assertRaises(ConfigurationError) as ctx:
            PipelineLoader.load_from_dict(cfg)
        self.assertIn("Bilinmeyen aşama türü", str(ctx.exception))

    def test_missing_required_parameter(self):
        """3. Zorunlu bir parametrenin eksik olması ConfigurationError fırlatmalıdır."""
        cfg = dict(self.valid_config)
        cfg["pipeline"] = dict(self.valid_config["pipeline"])
        # 'op' parametresi eksik filtre aşaması
        cfg["pipeline"]["stages"] = [
            {"type": "filter", "params": {"field": "status", "value": 400}}
        ]

        with self.assertRaises(ConfigurationError) as ctx:
            PipelineLoader.load_from_dict(cfg)
        self.assertIn("zorunlu 'op' parametresi eksik", str(ctx.exception))

    def test_invalid_parameter_type(self):
        """4. Yanlış türde parametre girilmesi ConfigurationError fırlatmalıdır."""
        cfg = dict(self.valid_config)
        cfg["pipeline"] = dict(self.valid_config["pipeline"])
        # 'fields' bir liste olmalıyken integer verilmiş
        cfg["pipeline"]["stages"] = [
            {"type": "project", "params": {"fields": 12345}}
        ]

        with self.assertRaises(ConfigurationError) as ctx:
            PipelineLoader.load_from_dict(cfg)
        self.assertIn("liste olmalıdır", str(ctx.exception))

    def test_empty_pipeline(self):
        """5. Hiç aşama içermeyen boş bir işlem hattı ConfigurationError fırlatmalıdır."""
        cfg = dict(self.valid_config)
        cfg["pipeline"] = dict(self.valid_config["pipeline"])
        cfg["pipeline"]["stages"] = []

        with self.assertRaises(ConfigurationError) as ctx:
            PipelineLoader.load_from_dict(cfg)
        self.assertIn("en az bir aşama (stage) içermelidir", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()