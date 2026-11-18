# Araçlar

- `video_sprite.py video.mp4 cikti.webp KARE GOVDE_PX` — magenta arka planlı 4K Flow videosunu ayıklanmış sprite sayfasına çevirir (bekleme 36, saldırı 18 kare; kule boyu 270 px). Çıktı satırı manifest bilgisidir.
- `sayfa_ekle.py kaynak/oyun.js manifest.txt` — sayfaları animasyon listesine ekler, bağlantı noktasını sabit kule görseline hizalar.
- `kule_yeri_oner.py bolum.json onizleme.png` — yola 115–160 px uzaklıkta, birbirinden en az 185 px ayrık kule yerleri önerir.
- `harita_rehber.py bolum.json cikti.png` — çizilecek harita için 3840×2160 yerleşim görseli.
- `bolum_simulasyonu.js BOLUM 'PLAN' cikti.png` — oyunu Playwright ile açar, bölümü çizimden bağımsız 0,05 sn adımlarla oynatan basit bir botla denge ölçer (yerel sunucu: `python3 -m http.server 8765`).
