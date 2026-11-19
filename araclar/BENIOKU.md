# Araçlar

- `video_sprite.py video.mp4 cikti.webp KARE GOVDE_PX [seçenekler]` — magenta (veya yeşil) arka planlı 4K Flow videosunu ayıklanmış sprite sayfasına çevirir (bekleme 36 kare; saldırı 30 kare ve `--aralik` ile — yalnızca atış anı alınır, vuruş karesi `hit` olarak yazılır; kule boyu 270 px; sonra `saldiri_hiza.py --yaz`). Çıktı satırı manifest bilgisidir. Seçenekler:
  - `--kenar SOL,SAG,UST,ALT` — efekt video kenarına değip kesiliyorsa o kenarı yumuşakça söndürür (px, 1920×1080 ölçeğinde). Kule gövdesi çoğu videoda üst/alt kenara yalnızca 20–40 px uzak: önce gövde payını ölçün, ona dokunmayın.
  - `--karisim` — yarı saydam buhar/duman/bulut/ışık halkalarında saydamlığı perde renginin baskınlığından hesaplar; pembe/mor hale bırakmaz. Kulede magenta/mor yoksa kullanın.
  - `--altin` / `--beyaz` — perdeyle karışıp pembeleşmiş efekt piksellerini parlaklığı koruyarak altın ya da nötr beyaz tona çeker (rün halkaları, maden tozu / buhar, bulut).
- `kare_sabitle.py` uyarısı: büyük halka, yağmur veya toz efektli sayfalarda kaideyi yanlış ölçer (efekt kaideye karışır); bu sayfalarda `--yaz` kullanmayın, kaymayı gövde dokusu eşlemesiyle doğrulayın.
- `sayfa_ekle.py kaynak/oyun.js manifest.txt` — sayfaları animasyon listesine ekler, bağlantı noktasını sabit kule görseline hizalar.
- `kule_yeri_oner.py bolum.json onizleme.png` — yola 115–160 px uzaklıkta, birbirinden en az 185 px ayrık kule yerleri önerir.
- `harita_rehber.py bolum.json cikti.png` — çizilecek harita için 3840×2160 yerleşim görseli.
- `bolum_simulasyonu.js BOLUM 'PLAN' cikti.png` — oyunu Playwright ile açar, bölümü çizimden bağımsız 0,05 sn adımlarla oynatan basit bir botla denge ölçer (yerel sunucu: `python3 -m http.server 8765`).

## Ortak çalışma notları (paralel oturumlar için)
- Push etmeden önce: `git pull --rebase origin main`, çakışmada `python3 kaynak/derle.py` ile index.html/sw.js yeniden üret.
- Savaş temposu: `OYUN_TEMPO` (0.85). Savaşta zamanla ilerleyen her şey `this.speed * OYUN_TEMPO` ile ölçeklenmeli
  (update dt, tweens.timeScale, kule saldırı animasyonu `anims.timeScale`). Yeni animasyon/efekt eklerken buna uy.
- Kule `rate` değerleri saniye cinsinden bekleme; 2026-11-19'da tüm saldırı kulelerinde ×1.4, hasar ×1.5 yapıldı.
- Sesler: ElevenLabs ücretsiz plan denemeleri `notlar/ucretsiz_sesler.txt` içinde listeli; yayından önce ücretli üretilecek.
