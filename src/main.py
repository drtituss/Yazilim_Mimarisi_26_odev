import argparse
import sys
from stages import FileLineSource, ConsoleSink, FileSink
from parser import ParserStage
from filters import PredicateFilterStage, ProjectionStage
from pipeline import PipelineBuilder
from loader import PipelineLoader
from interfaces import ConfigurationError, PipelineException

def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LogFlow Pipeline - Hata Yönetimi ve Dead-Letter Kanalı"
    )
    parser.add_argument("-c", "--config", help="YAML yapılandırma dosyası yolu (örn: configs/dirty-test.yaml)")
    parser.add_argument("input_file", nargs="?", help="İşlenecek log dosyası yolu (yalnızca manuel modda)")
    parser.add_argument("-o", "--output", help="Çıktının yazılacağı dosya yolu")
    parser.add_argument("--min-status", type=int, help="Yalnızca belirtilen HTTP durum kodu ve üzerini filtreler")
    parser.add_argument("--path-prefix", help="Yalnızca belirtilen yol öneki ile başlayanları filtreler")
    parser.add_argument("--fields", help="Virgülle ayrılmış projeksiyon alanları")
    return parser

def main():
    cli_parser = build_cli_parser()
    args = cli_parser.parse_args()

    # 1. Bildirimsel (Declarative) Yapılandırma Modu
    if args.config:
        try:
            pipeline = PipelineLoader.load_from_file(args.config)
            # pipeline.run() metodu çalışmayı tamamlayıp RunSummary tablosunu ekrana basar
            pipeline.run()
        except ConfigurationError as err:
            print(f"\n[YAPILANDIRMA HATASI] {err}\n", file=sys.stderr)
            sys.exit(1)
        except PipelineException as err:
            print(f"\n[KRİTİK İŞLEM HATASI] Boru hattı çalışmayı durdurdu: {err}\n", file=sys.stderr)
            sys.exit(1)
        return

    # 2. Manuel CLI Modu (Geriye Dönük Uyumluluk)
    if not args.input_file:
        cli_parser.print_help()
        sys.exit(1)

    try:
        source = FileLineSource(args.input_file)
        builder = PipelineBuilder.from_source(source)
        builder.via(ParserStage())

        if args.min_status is not None:
            builder.via(PredicateFilterStage(lambda r: r.status >= args.min_status))

        if args.path_prefix is not None:
            builder.via(PredicateFilterStage(lambda r: r.path.startswith(args.path_prefix)))

        if args.fields is not None:
            field_list = [f.strip() for f in args.fields.split(",")]
            builder.via(ProjectionStage(field_list))

        sink = FileSink(args.output) if args.output else ConsoleSink()
        pipeline = builder.to(sink)
        pipeline.run()
    except Exception as e:
        print(f"\n[HATA] Manuel mod çalıştırılamadı: {e}\n", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()