# LogFlow Pipeline - Increment 2

LogFlow is an extensible log processing engine built with the **Pipes and Filters** architectural pattern.

## Project Structure
- `src/`: Core interfaces and domain models (`interfaces.py`, `record.py`, `parser.py`, `stages.py`, `pipeline.py`, `main.py`).
- `tests/`: Unit test suite using the `CollectingEmitter` test double (`test_parser.py`).
- `data/`: Sample input files (`access-small.log`).
- `ARCHITECTURE.md`: Architectural decisions, separation of concerns, and component definitions.

## How to Run

### Run the Pipeline
```bash
python src/main.py data/access-small.log

```bash
python -m unittest discover -s tests

File,Statements,Miss,Coverage
src/interfaces.py,27,6,78%
src/parser.py,29,1,97%
src/record.py,17,2,88%
tests/test_parser.py,66,1,98%
TOTAL,139,10,93%

Change Log (Increment 2)
## Değişiklik Günlüğü (Increment 2)
- **Eklenen `src/record.py`:** Değişmez `LogRecord` alan modeli ve gelecekteki genişlemeler için `attributes` sözlüğü eklendi.
- **Eklenen `src/parser.py`:** Common Log Format (CLF) ayrıştırıcısı yazıldı; hatalı satırlar sayılıp atlanıyor.
- **Eklenen `tests/test_parser.py`:** Dosya okumadan bellekte çalışan 8 adet birim testi eklendi.
- **Güncellenen `src/stages.py`:** `ConsoleSink` artık ham metin yerine `LogRecord` nesnesi kabul ediyor.
- **Güncellenen `src/pipeline.py` & `src/main.py`:** Ayrıştırıcı aşama kaynak ile hedef arasına bağlandı.