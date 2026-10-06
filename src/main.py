import sys
from stages import FileLineSource, ConsoleSink
from pipeline import Pipeline

def main():
    # 1. Komut satırı argümanını oku
    if len(sys.argv) < 2:
        print("Kullanım: python src/main.py <dosya_yolu>")
        sys.exit(1)

    file_path = sys.argv[1]

    # 2. Pipeline'ı birleştir (assemble)
    source = FileLineSource(file_path)
    sink = ConsoleSink()
    pipeline = Pipeline(source, sink)

    # 3. Çalıştır (call run)
    pipeline.run()

if __name__ == "__main__":
    main()