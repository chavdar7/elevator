# Asansör Kontrol Sistemi Dokümantasyonu

## İçindekiler
1. [Sistem Genel Bakış](#sistem-genel-bakış)
2. [Dosya Yapısı](#dosya-yapısı)
3. [Kullanıcı Arayüzü Bileşenleri](#kullanıcı-arayüzü-bileşenleri)
4. [API Endpoints](#api-endpoints)
5. [JavaScript Fonksiyonları](#javascript-fonksiyonları)
6. [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)
7. [Sistem Özellikleri](#sistem-özellikleri)

---


## Sistem Genel Bakış

Sistemimizde -3'ten 12ye kadar 16 katlı bir binamız ve 2 asansörümüz var. Kullanıcılar sisteme ilk girdiğinde bulunduğu kattan çağrı oluşturacak yani gitmek istediği yönün tuşuna basacak. Uygun asansöre çağrı atanacak ve asansör çağrının geldiği kata gidecek. Sonrasında kullanıcı asansöre girecek, gideceği katın ve kilosunun bilgisini girecek. Asansör kilo kontrolü yapıp hedef kata gidecek ve yolcuyu indirecek. Yolcu inerken inen yolcunun kilo bilgisini sisteme girecek. Sistem Flask backend ile çalışıyor ve web üzerinden kontrol edebiliyoruz.

### Temel Özellikler
- **16 katlı bina** (-3 ile +12 arası)
- **2 asansör** (Asansör 1 ve Asansör 2)
- **Ağırlık kontrolü** (maksimum 130 kg)
- **Otomatik çağrı atama sistemi**
- **Canlı log sistemi**

---

## Dosya Yapısı

```
elevator-system/
├── index.html          # web arayüzünde görünen ana HTML sayfası
├── static/
│   ├── style.css       # CSS stilleri
│   └── script.js       # frontend ve backend bağlantılarını içeren js sayfası
├── app.py              # Flask backend sayfası, pagelerin bulun
└── elevator_logic.py   # Arka planda çalışan asansör mantığını içerir
```

- **/index.html**
  Kullanıcı arayüzünü içerir.
- **/style.css**
  index.html sayfasının css stilleri içerir.
- **/script.js**
  Frontend ve backend arası bağlantı kurar. API iletişimlerini sağlar.
- **/app.py**
  Main program sayfası. Flask backend içerir, pageleri tutar ve program burdan çalıştırılır.
- **/elevator_logic.py**
  Arka planda çalışan asansör algoritmasını içerir.
  

---

## Kullanıcı Arayüzü Bileşenleri

### 1. Ana Başlık Bölümü
Bütün sistemin içinde bulunduğu panelin başlığı:
**Asansör Kontrol Sistemi**

### 2. Kat Çağrıları Paneli
Sol üst tarafta bulunan panel(Asansör panelinin solunda). Asansör çağırma işlemi bu panelden gerçekleşiyor.
**Özellikler:**
- 16 kat için butonlar (-3 ile +12)
- Yukarı (↑) ve Aşağı (↓) çağrı butonları
- Otomatik buton devre dışı bırakma

### 3. Asansör Görüntü Panelleri
Sağ üst tarafta bulunan panel(Kat çağrıları panelinin sağında). Asansör takibi ve asansöre binme, inme işlemleri bu panelden gerçekleşiyor.
Her asansör için:
- **Dijital ekran**: Mevcut kat ve yön göstergesi
- **Ağırlık göstergesi**: Mevcut yük (kg)
- **Durum göstergesi**: Boş, Hareket Ediyor, Kapı Açık
- **Hedef listesi**: Gidilecek katlar
- **Kontrol butonları**: "Asansöre Bin" ve "Yolcu İndir"

### 4. Sistem Kontrol Paneli
Alt tarafta bulunan panel(Asansör ve kat çağrı panellerinin altında). Sistemin aktiflik durumunu ve anlık olarak log mesajlarını görüntüler.
- **Sistem durumu**: Aktif/Pasif
- **Bekleyen çağrı sayısı**
- **Yenile** ve **Test** butonları
- **Canlı log sistemi**: Son 20 işlem

### 5. Modal Pencereler
#### Asansöre Binme Modalı
Asansöre bin butonuna basıldığında açılır. Kilonuzu ve hedef katı girmeniz gerekir.
```html
<label>Hedef Kat: <input type="number" min="-3" max="12"></label>
<label>Kilonuz (kg): <input type="number" min="1" max="130"></label>
```

#### Yolcu İndirme Modalı
Yolcu indir butonuna basıldığında açılır. İnen yolcunun kilosunu girmeniz gerekir.
```html
<label>Kilo (kg): <input type="number" min="1" max="130"></label>
```

---

## API Endpoints

### Çağrı Yapma
```
GET /api/cagri/{kat}/{yon}
```
**Parametreler:**
- `kat`: -3 ile 12 arası
- `yon`: "yukarı" veya "aşağı"

**Yanıt:**
```json
{
  "durum": "atandi",
  "mesaj": "Asansör 1 size geliyor"
}
```

### Hedef Kat Belirleme
```
GET /api/hedef/{asansor_id}/{hedef_kat}?kilo={kilo}
```
**Parametreler:**
- `asansor_id`: 1 veya 2
- `hedef_kat`: -3 ile 12 arası
- `kilo`: 1-130 kg arası

### Yolcu İndirme
```
GET /api/indi/{asansor_id}?kilo={kilo}
```
**Parametreler:**
- `asansor_id`: 1 veya 2
- `kilo`: 1-130 kg arası

### Sistem Durumu
```
GET /api/durum
```
**Yanıt:**
```json
{
  "asansor_1": {
    "kat": 5,
    "yon": "yukarı",
    "yuk": 75,
    "durum": "hareket_ediyor",
    "hedefler": [8, 12]
  },
  "asansor_2": { /* ... */ },
  "bekleyen_cagrilar": 2
}
```

### Test Endpoint
```
GET /test
```
**Yanıt:**
```json
{
  "message" : "Flask başarılı",
  "asansor_sayisi" : 2,
  "kat_sayisi" : 16
}
```

---

## JavaScript Fonksiyonları

### Ana Fonksiyonlar

#### `createFloorButtons()`
- Kat butonlarını dinamik olarak oluşturur
- 12'den -3'e kadar katları listeler
- Her kata uygun yön butonları ekler

#### `callElevator(kat, yon)`
- Asansör çağrısı yapar
- Butonları geçici olarak devre dışı bırakır
- API'ye istek gönderir
- Log mesajı ekler

#### `refreshSystem()`
- Sistem durumunu API'den alır
- Asansör görsellerini günceller
- Log mesajlarını işler

#### `updateElevatorDisplays()`
- Her iki asansörün görselini günceller
- Kat, yön, ağırlık ve durum bilgilerini yeniler


### Yardımcı Fonksiyonlar

#### `addLog(message, withTimestamp)`
- Log containerına mesaj ekler
- Maksimum 20 log tutar
- Otomatik scroll

#### `startAutoRefresh()` / `stopAutoRefresh()`
- 3 saniyede bir otomatik yenileme
- Sayfa kapatılırken durdurur

---

## Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.x
- Flask framework
- Modern web tarayıcı

### Adımlar
1. **Dosyaları yerleştir**:
   ```
   project/
   ├── elevator_logic.py
   ├── app.py
   ├── templates/
   │   └── index.html
   └── static/
       ├── style.css
       └── script.js
   ```

2. **Flask uygulamasını çalıştır**:
   ```bash
   python app.py
   ```

3. **Tarayıcıda aç**:
   ```
   http://localhost:5000
   ```

---

## Sistem Özellikleri

- **Ağırlık kontrolü**: 130 kg üst limit
- **Kat sınırlaması**: -3 ile +12 arası
- **Button debouncing**: Çift tıklama önleme
- **Anlık geri bildirim**: Log mesajları
- **Visual feedback**: Buton durumu değişimi
- **Loading states**: "wait" göstergesi
- **Error handling**: Hata mesajları
- **Otomatik yenileme**: 3 saniyede bir

---