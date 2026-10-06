# Architectural Overview - Increment 2: Typed Records & First Filter

## Three-Box Architecture Diagram
```
+---------------------+               +---------------------+               +---------------------+
|                     |   str (raw)   |                     |   LogRecord     |                     |
|   FileLineSource    | ------------> |     ParserStage     | ------------> |     ConsoleSink     |
|  (Source Component) |               |  (Filter Component) |  (Domain Model)|   (Sink Component)  |
+---------------------+               +---------------------+               +---------------------+
```

## Architectural Concepts

### 1. Shift from Raw Strings to Domain Model
- Increment 1'de boru hattı ham `str` taşıyordu[cite: 1]. Increment 2 ile birlikte boru hattı tip güvenli, değişmez (`immutable`) bir `LogRecord` alan modeli taşır hale getirildi.
- Bu dönüşüm sayesinde sonraki aşamalar regex veya metin parçalamayla uğraşmaz; doğrudan tipli alanlara (`client_ip`, `status`, `bytes`, `timestamp`) erişir.

### 2. Extensibility (`attributes` Map)
- `LogRecord` içindeki `attributes: Dict[str, str]` sözlüğü, Open/Closed Principle gereği sonraki haftalar (Hafta 5-7) için bilinçli olarak bırakılmış bir genişleme noktasıdır.
- İleride eklenecek filtreler temel veri yapısını bozmadan ekstra verileri buraya ekleyebilecektir.

### 3. Separation of Concerns & Test Doubles
- `ParserStage` diskten bağımsızdır; girdi olarak sadece metin alır ve `Emitter` ile `LogRecord` nesnesi yayar[cite: 1].
- Birim testlerinde disk I/O yapmamak için `CollectingEmitter` test dublörü kullanılmıştır. Bu sayede testler harici dosyalardan bağımsız, hızlı ve kararlı çalışır.