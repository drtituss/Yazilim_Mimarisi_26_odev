# LogFlow Pipeline - Increment 4

LogFlow is an extensible, modular log processing engine built with the **Pipes and Filters** architectural pattern and driven by declarative YAML configurations.

## Project Structure
- `src/`:
  - `interfaces.py`: Core Source, Sink, Stage abstractions and `ConfigurationError`.
  - `record.py`: Immutable `LogRecord` domain model.
  - `parser.py`: Common Log Format (CLF) parser stage.
  - `filters.py`: `PredicateFilterStage` (condition-based) and `ProjectionStage`.
  - `stages.py`: `FileLineSource`, `ConsoleSink`, and `FileSink`.
  - `pipeline.py`: Pipeline execution engine and fluent `PipelineBuilder`.
  - `registry.py`: Data-driven `StageRegistry` mapping stage names to factories.
  - `loader.py`: Declarative YAML loader with fail-fast validation.
  - `main.py`: CLI entry point supporting both `--config` and manual arguments.
- `configs/`:
  - `error-report.yaml`: Filters HTTP status >= 400.
  - `api-traffic.yaml`: Extracts `/api` traffic.
  - `bandwidth-client.yaml`: Extracts client bandwidth for requests > 500 bytes.
- `tests/`:
  - `test_parser.py`: Parser unit tests (8 edge cases).
  - `test_stages.py`: Unit tests for PredicateFilter, Projection, and FileSink.
  - `test_integration.py`: End-to-end integration test.
  - `test_loader.py`: Validation tests for declarative configuration loader.
- `ARCHITECTURE.md`: Architectural documentation, registry design, and YAML schema.

---

## How to Run

### Run Pre-Configured Declarative Pipelines
```bash
# 1. Error Report
python src/main.py --config configs/error-report.yaml

# 2. API Traffic Extract
python src/main.py --config configs/api-traffic.yaml

# 3. Client Bandwidth Extract
python src/main.py --config configs/bandwidth-client.yaml