import java.util.ArrayList;
import java.util.List;

public class Pipeline<T> {
    private final Source<T> source;
    private final Sink<T> sink;
    private final List<Stage<T, T>> stages;

    public Pipeline(Source<T> source, Sink<T> sink) {
        this.source = source;
        this.sink = sink;
        this.stages = new ArrayList<>();
    }

    public Pipeline<T> addStage(Stage<T, T> stage) {
        stages.add(stage);
        return this;
    }

    public void run() {
        // 1. Yaşam döngüsü: Varsa tüm aşamaların open() metodunu tetikle
        for (Stage<T, T> stage : stages) {
            stage.open();
        }

        // 2. Kaynaktan veriyi üretmeye başla ve ilk aşamaya gönder
        source.produce(item -> dispatch(item, 0));

        // 3. Yaşam döngüsü: İşlem bitince close() kancalarını çalıştır
        for (Stage<T, T> stage : stages) {
            stage.close();
        }
    }

    private void dispatch(T currentItem, int stageIndex) {
        // Eğer tüm filtreler/aşamalar bittiyse veriyi doğrudan Sink'e ilet
        if (stageIndex >= stages.size()) {
            sink.consume(currentItem);
            return;
        }

        Stage<T, T> currentStage = stages.get(stageIndex);
        try {
            // Aşamayı çalıştır; aşama veri yaydıkça (emit ettikçe) sonraki aşamaya devret
            currentStage.process(currentItem, nextItem -> dispatch(nextItem, stageIndex + 1));
        } catch (StageException e) {
            System.err.println("Pipeline işlem hatası: " + e.getMessage());
        }
    }
}