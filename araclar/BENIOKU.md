# Araçlar

- `video_sprite.py video.mp4 cikti.webp KARE GOVDE_PX [seçenekler]` — magenta (veya yeşil) arka planlı 4K Flow videosunu ayıklanmış sprite sayfasına çevirir (bekleme 36, saldırı 18 kare; kule boyu 270 px). Çıktı satırı manifest bilgisidir. Seçenekler:
  - `--kenar SOL,SAG,UST,ALT` — efekt video kenarına değip kesiliyorsa o kenarı yumuşakça söndürür (px, 1920×1080 ölçeğinde). Kule gövdesi çoğu videoda üst/alt kenara yalnızca 20–40 px uzak: önce gövde payını ölçün, ona dokunmayın.
  - `--karisim` — yarı saydam buhar/duman/bulut/ışık halkalarında saydamlığı perde renginin baskınlığından hesaplar; pembe/mor hale bırakmaz. Kulede magenta/mor yoksa kullanın.
  - `--altin` / `--beyaz` — perdeyle karışıp pembeleşmiş efekt piksellerini parlaklığı koruyarak altın ya da nötr beyaz tona çeker (rün halkaları, maden tozu / buhar, bulut).
- `kare_sabitle.py` uyarısı: büyük halka, yağmur veya toz efektli sayfalarda kaideyi yanlış ölçer (efekt kaideye karışır); bu sayfalarda `--yaz` kullanmayın, kaymayı gövde dokusu eşlemesiyle doğrulayın.
- `sayfa_ekle.py kaynak/oyun.js manifest.txt` — sayfaları animasyon listesine ekler, bağlantı noktasını sabit kule görseline hizalar.
- `kule_yeri_oner.py bolum.json onizleme.png` — yola 115–160 px uzaklıkta, birbirinden en az 185 px ayrık kule yerleri önerir.
- `harita_rehber.py bolum.json cikti.png` — çizilecek harita için 3840×2160 yerleşim görseli.
- `bolum_simulasyonu.js BOLUM 'PLAN' cikti.png` — oyunu Playwright ile açar, bölümü çizimden bağımsız 0,05 sn adımlarla oynatan basit bir botla denge ölçer (yerel sunucu: `python3 -m http.server 8765`).
