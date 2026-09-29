public interface Stage<I, O> {
    void process(I input, Emitter<O> out) throws StageException;
    default void open() { } // İlerideki haftalarda kaynak açmak için yaşam döngüsü kancası
    default void close() { } // Kaynakları kapatmak için kanca
}