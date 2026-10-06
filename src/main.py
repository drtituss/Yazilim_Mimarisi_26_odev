import sys
from stages import FileLineSource, ConsoleSink
from parser import ParserStage
from pipeline import Pipeline

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python src/main.py <dosya_yolu>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Pipeline Montajı
    source = FileLineSource(file_path)
    sink = ConsoleSink()
    parser_stage = ParserStage()

    pipeline = Pipeline(source, sink)
    pipeline.add_stage(parser_stage)  # FileLineSource -> ParserStage -> ConsoleSink

    # Çalıştır
    pipeline.run()

if __name__ == "__main__":
    main()