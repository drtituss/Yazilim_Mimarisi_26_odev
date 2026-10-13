import argparse
import sys
from stages import FileLineSource, ConsoleSink, FileSink
from parser import ParserStage
from filters import PredicateFilterStage, ProjectionStage
from pipeline import PipelineBuilder

def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LogFlow Pipeline - CLI Log Filtreleme ve Dönüştürme Aracı"
    )
    parser.add_argument("input_file", help="İşlenecek log dosyası yolu (örn: data/access-small.log)")
    parser.add_argument("-o", "--output", help="Çıktının yazılacağı dosya yolu (verilmezse konsola yazar)")
    parser.add_argument("--min-status", type=int, help="Yalnızca belirtilen HTTP durum kodu ve üzerini filtreler (örn: 400)")
    parser.add_argument("--path-prefix", help="Yalnızca belirtilen yol öneki ile başlayanları filtreler (örn: /api)")
    parser.add_argument("--fields", help="Virgülle ayrılmış projeksiyon alanları (örn: timestamp,client_ip,status,path)")
    return parser

def main():
    cli_parser = build_cli_parser()
    args = cli_parser.parse_args()

    # 1. Kaynak ve Kurucu Başlatma
    source = FileLineSource(args.input_file)
    builder = PipelineBuilder.from_source(source)

    # 2. Ayrıştırma Aşaması (Metinden LogRecord nesnesine)
    builder.via(ParserStage())

    # 3. Koşullu Filtreler (PredicateFilterStage)
    if args.min_status is not None:
        builder.via(PredicateFilterStage(lambda r: r.status >= args.min_status))

    if args.path_prefix is not None:
        builder.via(PredicateFilterStage(lambda r: r.path.startswith(args.path_prefix)))

    # 4. Projeksiyon Aşaması (Alan Seçimi / Veri Minimizasyonu)
    if args.fields is not None:
        field_list = [f.strip() for f in args.fields.split(",")]
        builder.via(ProjectionStage(field_list))

    # 5. Hedef Bileşen (FileSink veya ConsoleSink)
    sink = FileSink(args.output) if args.output else ConsoleSink()
    pipeline = builder.to(sink)

    # 6. Boru Hattını Çalıştır
    pipeline.run()

if __name__ == "__main__":
    main()