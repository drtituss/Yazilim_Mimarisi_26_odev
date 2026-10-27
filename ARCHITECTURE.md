# Architectural Overview - Increment 5: Error Management & Dead-Letter Channel

## 1. Error Model (Hata Modeli ve Yalıtımı)
Hata yönetimi sadece bir `try/catch` bloğu değil, mimari bir karardır. Sistemde iki farklı istisna seviyesi tasarlanmıştır:
* **`StageException` (Kurtarılabilir Hata):** Tek bir kayıt (log satırı) işlenirken ayrıştırma, format veya doğrulama ihlali oluştuğunda fırlatılır. İşlem hattı çöktürülmez; kayıt hatalı işaretlenerek yapılandırılan `ErrorPolicy`'ye (örn. `DEAD_LETTER` veya `SKIP`) devredilir.
* **`PipelineException` (Kurtarılamaz Kritik Hata):** Dosyanın bulunamaması, diskin dolması, yetki eksikliği veya konfigürasyon hataları gibi tüm sistemin devamlılığını tehdit eden durumlarda fırlatılır. `FAIL_FAST` ilkesi gereği boru hattı anında durdurulur ve çöktürülür.

## 2. Topoloji: Dead-Letter Channel (İkincil Çıktı Yolu)
Hata yönlendirmesi bir topolojik karardır. Boru hattı (pipeline) artık düz bir çizgi olmaktan çıkmış, hatalı kayıtlar için tasarlanmış ikincil bir rotaya (Y-ayrımına) sahip olmuştur.

```text
                           [ FileLineSource ] (errors="replace")
                                  |
                                  v
                            [ ParserStage ] --(StageException + DEAD_LETTER)--> [ DeadLetterFileSink ]
                                  |                                                (out/dead-letter.log)
                                  v
                          [ ValidationStage ] --(StageException + DEAD_LETTER)--> [ DeadLetterFileSink ]
                                  |
                                  v
                           [ Filter & Project ]
                                  |
                                  v
                             [ FileSink ] (Ana Hedef)
```

## 3. Chaos Test Error Policy Mapping (Kaos Testi Hata Tablosu)
Bozuk veri setindeki (`access-dirty.log`) kayıtların sistem tarafından nasıl yönetildiği aşağıda eşleştirilmiştir:

| Hata Türü (Bozuk Veri) | Yakalayan Aşama | Uygulanan Politika | Sonuç (Yönlendirme) |
| :--- | :--- | :--- | :--- |
| UTF-8 Olmayan Bayt (`0xff`) | `FileLineSource` (Replace) + `ParserStage` | `DEAD_LETTER` (Parser Regex İhlali) | `out/dead-letter.log` |
| Kesilmiş / Yarım Satır | `ParserStage` | `DEAD_LETTER` (Regex Eşleşmemesi)| `out/dead-letter.log` |
| Boş Dosya / Boş Satır | `ParserStage` | `DEAD_LETTER` (Boş İçerik Hatası)| `out/dead-letter.log` |
| Negatif Bayt Değeri | `ParserStage` veya `ValidationStage` | `DEAD_LETTER` | `out/dead-letter.log` |
| 1970 veya 2099 Zaman Damgası | `ValidationStage` | `DEAD_LETTER` (Aralık İhlali) | `out/dead-letter.log` |
| Geçersiz IP Biçimi | `ValidationStage` | `DEAD_LETTER` (Regex İhlali) | `out/dead-letter.log` |

*Not: Sistem hiçbir hata senaryosunda çökmeyerek (graceful degradation) çalışmasını tamamlamış ve `RunSummary` üzerinden tüm bozuk satırları hesaba katmıştır.*                                                                                                                                                                                              