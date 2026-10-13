# Architectural Overview - Increment 3: Composition, Stages & PipelineBuilder

## Multi-Stage Pipeline Architecture Diagram
```
+------------------+         +---------------+         +------------------------+         +-----------------+         +-------------+
|  FileLineSource  | --str-> |  ParserStage  | -Record-> | PredicateFilterStage   | -Record-> | ProjectionStage | -Dict->   |  FileSink   |
| (Source / Disk)  |         | (Parse to Rec)|         | (e.g. status >= 400)   |         | (Minimization)  |           | (Sink/Disk) |
+------------------+         +---------------+         +------------------------+         +-----------------+         +-------------+
```

---

## Architectural Concepts

### 1. Fluent PipelineBuilder Pattern
- Aşamaların birbirine manuel bağlanması yerine Akıcı Arayüz (Fluent Interface) deseni geliştirilmiştir.
- `PipelineBuilder.from_source(source).via(stage1).via(stage2).to(sink)` zinciri okunabilirliği ve bileşilebilirliği (composability) artırır.

### 2. Lifecycle Hooks & Resource Safety
- `FileSink` bileşeni `open()` ve `close()` kancalarını uygular.
- `Pipeline.run()` içerisindeki `try ... finally` güvencesi sayesinde, ara aşamalarda hata meydana gelse dahi `close()` kancası tetiklenir, işletim sistemi tamponundaki (buffer) log verileri diske yazılır ve kaynak sızıntısı önlenir.

---

## Stage Ordering Experiment & Trade-off Analysis (Sıralama Deneyi ve Ödünleşim)

Boru hattı bileşenlerinin yer değiştirilebilirliği (composability) deneysel olarak test edilmiş ve şu sonuçlara ulaşılmıştır:

### 1. Ayrıştırma Öncesi Filtreleme İmkânsızlığı
- `FileLineSource` ham `str` üretirken, `PredicateFilterStage` tip güvenli `LogRecord` alanlarını (ör. `r.status`, `r.path`) denetler.
- Dolayısıyla `ParserStage` her zaman mantıksal filtrelerden önce gelmek zorundadır.

### 2. Filtreleme ve Projeksiyon Sıralaması (Filter vs. Projection Trade-off)
İki farklı çalıştırma sırası test edilmiştir:
- **Sıra A (Önce Filtre, Sonra Projeksiyon):** `Parser -> PredicateFilterStage -> ProjectionStage -> FileSink`
- **Sıra B (Önce Projeksiyon, Sonra Filtre):** `Parser -> ProjectionStage -> PredicateFilterStage -> FileSink`

#### Sonuç ve Ödünleşim Karşılaştırması:
1. **İşlevsel Eşdeğerlik:** İki sıra da doğru konfigüre edildiğinde nihai çıktı kümesi olarak **aynı sonuçları üretir**.
2. **Performans ve Bellek Verimliliği:** 
   - **Sıra A çok daha üstündür.** Koşulu sağlamayan kayıtlar (ör. 10.000 kaydın %90'ı) henüz filtre aşamasındayken elenir. Bu sayede elenen kayıtlar için gereksiz yere `dict` projeksiyonu oluşturulmaz, bellek tahsisi (allocation) yapılmaz ve CPU döngüsü harcanmaz.
   - **Sıra B'de** ise tüm kayıtlar önce gereksiz yere projeksiyon işlemine tabi tutulur, ardından elenir; bu da yüksek veri akışında ciddi bir performans kaybına yol açar.
3. **Tip Güvenliği Bağımlılığı:** 
   - Filtreleme önce yapıldığında `PredicateFilterStage` doğrudan tip güvenli `LogRecord` üzerinde çalışır.
   - Projeksiyon öne alınırsa kayıt artık `dict` tipine dönüşeceğinden, filtrenin ihtiyaç duyduğu alanlar projeksiyonda unutulduğu takdirde filtre `KeyError` verir veya hatalı çalışır.