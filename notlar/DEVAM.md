# Devam notu (yarıda kalırsa buradan sürdür)
Kullanıcı isteği (19.11 23:07): eksik özellikleri yaz; her biri sanatsal, "vay be" dedirtsin.
Sıra:
1. [x] Emanetler — 8 eşya (assets/emanet_*.webp hazır). Boss/bölüm ilk zaferinde düşer; 2 yuva; Şan Salonu penceresi.
2. [x] Başarımlar — 12 (assets/basarim_*.webp). Her biri +1 Taç Puanı; oyun içinde altın şerit duyurusu.
3. [x] Zorluk modları — Kahramanca / Demir (rozet_*.webp); brifingde seçim, haritada düğüm rozetleri.
4. [x] Sonsuz Kuşatma — harita assets/harita_sonsuz_tam_a/b.webp, yerleşim notlar/harita_sonsuz.json; yollar araclar/yol_uydur.py ile uydurulacak.
5. [x] Füzyon kuleleri — kule_fuzyon_*.webp sabit resimler var, saldırı videoları kısmen.
Test: scratchpad t_*.js sürücüleri; yerel sunucu `python3 -m http.server 8765`.
6. [x] Günlük Meydan Okuma — tarihe bağlı bölüm + kural (7 kural), seri, rozet_gunluk, hazine+elmas; kule yasaklayan kural elde az kule bırakıyorsa sıradaki kurala geçer.
Kod tarafında yazılacak özellik kalmadı. Bekleyen: Flow animasyonları (kullanıcının arkadaşı), telefon geri bildirimi, yayın öncesi 119 sesi ücretli ElevenLabs'te yeniden üretmek.

## Gece planı (20.11, kullanıcı uyuyor — sırayla yap, her biri bitince test + commit + push)
Geri bildirimler: müzik yorucu / zaferde müzik sürüyor (YAPILDI 78422de), sonuç ekranı küçük, öğretici zayıf,
hikâye zayıf, savaş ambiyansı sönük ("düz fotoğraf"), kahraman sesi önerisi.
Kullanıcının uyarısı: ezbere gitme; senarist gibi kurgula, sanatçı gibi işle. Kodla çizilen efektler zayıf kaldı.
1. [x] Rehber (haritada kahramanlar özellikleri zamanı gelince gösterir) — 8736a6b
2. [x] Hikâye yeniden yazıldı (notlar/senaryo.md; dlg.* ve vaka.*.metin, {hitap}/{k}) — vakayiname kutusuna sığıyor mu
       kontrol et (metinler uzadı), diyalog ekranını test et, commit.
3. [x] Flow videolarından efekt ayıkla (kullanıcı önerisi): saldırı videolarındaki buz patlaması, şimşek, ateş topu,
       zehir bulutu → kuleden bağımsız efekt sayfaları (ADD karışım) → büyü/vuruş efektlerinde kullan. Kodla çizim değil.
4. [x] Sonuç ekranı tam ekran ve görkemli (zafer/yenilgi).
5. [ ] Hazine ve Elmas hiçbir yerde harcanmıyor — anlamlı kullanım tasarla (ör. hazine: kahraman eğitimi,
       elmas: emanet güçlendirme) ve rehbere ekle.
6. [ ] Ambiyans: canlı harita altyapısı (Rt, harita_stageN_canli video+maske) hangi bölümlerde var çıkar;
       eksikler için Flow prompt paketi; kodla yalnızca ince ışık/renk/vinyet.
7. [ ] Kullanıcıya tek paket: savaş müziği varyasyonları (rotasyon), kahraman ses replikleri (ElevenLabs),
       canlı harita Flow promptları.
