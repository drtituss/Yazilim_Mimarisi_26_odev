public class ConsoleSink implements Sink<String> {
    @Override
    public void consume(String item) {
        System.out.println(item);
    }
}