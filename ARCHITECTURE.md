# Architectural Overview - Increment 4: Declarative Configuration & Stage Registry

## Declarative Architecture Diagram
```
                          +-------------------------+
                          |   pipeline.yaml (DSL)   |
                          +-------------------------+
                                       |
                                       v
                             [ PipelineLoader ]  <--- (Fail Fast Validation)
                                       |
                     +-----------------+-----------------+
                     |                                   |
                     v                                   v
             [ StageRegistry ]                  [ PipelineBuilder ]
           (Dynamic Factory Map)                         |
                     |                                   v
                     +----------------------------> [ Pipeline Engine ]
                                                         |
                  +--------------------------------------+--------------------------------------+
                  |                                      |                                      |
                  v                                      v                                      v
         [ FileLineSource ]                     [ Processing Stages ]                     [ FileSink ]
```

---

## Architectural Concepts

### 1. Separation of Architectural Definition from Implementation
- İşlem hattının topolojisi ve veri akışı koddan soyutlanarak bildirimsel (declarative) YAML dosyalarına aktarılmıştır.
- **Kilometre Taşı Avantajı:** Yeni bir filtreleme veya analiz boru hattı kurmak için kod değişikliği veya yeniden derleme/dağıtım gerekmez; yalnızca yeni bir YAML yapılandırma dosyası tanımlanır.

### 2. Stage Registry Pattern (Veri Odaklı Eşleme)
- Kod içinde katı, sabit kodlanmış (`hardcoded`) `switch-case` veya zincirleme `if-else` blokları kullanılmamıştır.
- `StageRegistry` sınıfı, aşama adlarını karşılık gelen fabrika (factory) fonksiyonlarına bir sözlük eşlemi (`Map/Dictionary`) üzerinden bağlar.
- Yeni bir aşama eklendiğinde yalnızca `register_stage` metoduyla kayıt defterine tanımlanması yeterlidir (Açık/Kapalı Prensibi - OCP).

### 3. Fail Fast, Fail Loudly (Erken ve Gürültülü Başarısızlık)
- **Yapılandırma Zamanı (Config-Time) Hataları:** Dosya yolu eksikliği, bilinmeyen aşama adı, eksik parametre (`op`, `field` vb.) veya hatalı veri tipleri boru hattı inşa edilmeden önce `PipelineLoader` tarafından yakalanır ve net bir `ConfigurationError` fırlatılır. Tek bir satır log dahi işlenmeden süreç güvenle durdurulur.
- **Çalışma Zamanı (Runtime) Veri Hataları:** Bozuk log satırları veya ağ/disk kesintileri ise veri akışı esnasında `StageException` ile yönetilir.

---

## Configuration Schema (YAML Şeması)

```yaml
pipeline:
  name: <string>              # Boru hattı kimliği/açıklaması
  source:
    type: file                # Kaynak tipi: 'file'
    params:
      path: <string>          # Okunacak dosya yolu
  stages:
    - type: parse             # Ayrıştırıcı aşama
      params:
        format: clf           # Desteklenen format: 'clf'
    - type: filter            # Koşullu filtreleme
      params:
        field: <string>       # LogRecord alanı (status, path, bytes vb.)
        op: <string>          # Karşılaştırma operatörü: '>=', '<=', '==', '!=', 'startswith', 'contains'
        value: <any>          # Karşılaştırma değeri
    - type: project           # Veri minimizasyonu / projeksiyon
      params:
        fields: [<string>]    # Seçilecek alan listesi
  sink:
    type: file | console      # Hedef bileşen tipi
    params:
      path: <string>          # Çıktı dosya yolu ('file' seçildiyse zorunlu)
```