public class Main {
    public static void main(String[] args) {
        // 1. Komut satırı argümanını oku
        if (args.length < 1) {
            System.err.println("Kullanım: java Main <dosya_yolu>");
            System.exit(1);
        }

        String logFilePath = args[0];

        // 2. Pipeline'ı birleştir (assemble)
        Source<String> source = new FileLineSource(logFilePath);
        Sink<String> sink = new ConsoleSink();

        Pipeline<String> pipeline = new Pipeline<>(source, sink);

        // 3. run() çağır
        pipeline.run();
    }
}