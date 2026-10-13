# LogFlow Pipeline - Increment 3

LogFlow is an extensible, modular log processing engine built with the **Pipes and Filters** architectural pattern.

## Project Structure
- `src/`:
  - `interfaces.py`: Core Source, Sink, Stage, and Emitter abstractions.
  - `record.py`: Immutable `LogRecord` domain model.
  - `parser.py`: Common Log Format (CLF) parser stage.
  - `filters.py`: `PredicateFilterStage` and `ProjectionStage`.
  - `stages.py`: `FileLineSource`, `ConsoleSink`, and `FileSink`.
  - `pipeline.py`: Pipeline execution engine and fluent `PipelineBuilder`.
  - `main.py`: Configurable command-line interface (CLI).
- `tests/`:
  - `test_parser.py`: Parser stage unit tests with 8 distinct edge cases.
  - `test_stages.py`: Unit tests for PredicateFilter, Projection, and FileSink lifecycle.
  - `test_integration.py`: End-to-end integration test validating pipeline output.
- `ARCHITECTURE.md`: Architectural documentation and Stage Ordering experiment analysis.

---

## How to Run

### Command-Line Interface (CLI)
```bash
# Filter by status code and print to console
python src/main.py data/access-small.log --min-status 400

# Filter by prefix and project specific fields to a file
python src/main.py data/access-small.log --path-prefix /api --fields timestamp,client_ip,status,path -o data/output.log