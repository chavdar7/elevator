import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AsansorDurum(Enum):
    BOS = "boş"
    HAREKET_EDIYOR = "hareket_ediyor"
    KAPI_ACIK = "kapı_açık"
    ARIZALI = "arızalı"

class Yon(Enum):
    YUKARI = "yukarı"
    ASAGI = "aşağı"
    DURGUN = "durgun"

#asansör çağrısı - nereden geldi ve hangi yöne
@dataclass
class Cagri:
    cagri_kati : int
    yon : Yon
    zaman_d : float
    durum : str = "bekliyor"

#asansör sınıfı
@dataclass
class Asansor:
    id : int
    mevcut_kat : int = 0
    hedef_katlar : List[int] = None
    yon : Yon = Yon.DURGUN
    durum : AsansorDurum = AsansorDurum.BOS
    mevcut_yuk : float = 0.0
    kapi_acilma_zamani : float = 0.0

    def __post_init__(self):
        if self.hedef_katlar is None:
            self.hedef_katlar = []


#ana asansör sistemi
class AsansorSistemi:
    def __init__(self):
        self.asansor_1 = Asansor(id=1)
        self.asansor_2 = Asansor(id=2)
        self.bekleyen_cagrilar : List[Cagri] = []
        self.aktif_cagrilar : List[Cagri] = []
        self.log_mesajlari : List[str] = []
        self.son_hareket_zamani = 0
        self.son_log_sayisi = 0

        print("Asansör sistemi başlatılıyor")
        print("2 asansör(130kg kapasite), -3ten 12ye toplam 16 kat.")

    #sistem durumunu dict olarak döndürecek(frontendde)
    def sistem_durumu(self) -> Dict:
        return{
            'asansor_1' : {
                'id': self.asansor_1.id,
                'kat': self.asansor_1.mevcut_kat,
                'yon': self.asansor_1.yon.value,
                'durum': self.asansor_1.durum.value,
                'yuk': self.asansor_1.mevcut_yuk,
                'hedefler': self.asansor_1.hedef_katlar.copy()
            },
            'asansor_2' : {
                'id': self.asansor_2.id,
                'kat': self.asansor_2.mevcut_kat,
                'yon': self.asansor_2.yon.value,
                'durum': self.asansor_2.durum.value,
                'yuk': self.asansor_2.mevcut_yuk,
                'hedefler': self.asansor_2.hedef_katlar.copy()
            },
            'bekleyen_cagrilar' : len(self.bekleyen_cagrilar),
            'log_mesajlari' : self._yeni_log_mesajlari()
        }
    
    #log mesajı ekleyecek
    def log_ekle(self, mesaj:str):
        zaman = time.strftime("%H:%M:%S")
        self.log_mesajlari.append(f"[{zaman}] {mesaj}")
        print(f"[{zaman}] {mesaj}")

    #Yeni asansör çağrısı(nereden ve hangi yöne) => (kullanıcı kat butonuna basıyor)
    def cagri_yap(self, cagri_kati:int, yon: str) -> Dict:
        
        #girdi kontrol
        if not (-3 <= cagri_kati <= 12):
            return {'hata' : 'geçersiz kat numarası'}
        
        if yon not in ['yukarı','aşağı']:
            return {'hata' : 'geçersiz yön'}
        
        #çağrı oluşturcaz
        yeni_cagri = Cagri(
            cagri_kati= cagri_kati,
            yon = Yon.YUKARI if yon == 'yukarı' else Yon.ASAGI,
            zaman_d = time.time() 
        )

        self.log_ekle(f"{cagri_kati}. kattan {yon} çağrısı geldi.")

        #asansör seçelim
        secilen_asansor = self._asansor_sec(yeni_cagri)

        if secilen_asansor is None : #hiçbir asansör uygun değilse bekleme listesine ekler
            self.bekleyen_cagrilar.append(yeni_cagri)
            self.log_ekle("Çağrınız bekleme listesine alındı")
            return{
                'durum' : 'beklemede',
                'mesaj' : f'tüm asansörler meşgul. sıradaki {len(self.bekleyen_cagrilar)}'
            }
        else: #asansöre çağrıyı ata
            self._cagri_ata(secilen_asansor, yeni_cagri)
            return{
                'durum' : 'atandı',
                'asansor_id' : secilen_asansor.id,
                'mesaj' : f'Asansör {secilen_asansor.id} geliyor.'
            }

    #en uygun asansörü seçecek    
    def _asansor_sec(self, cagri: Cagri) -> Optional[Asansor]:
        asansor_1_skor = self._asansor_skorla(self.asansor_1, cagri)
        asansor_2_skor = self._asansor_skorla(self.asansor_2, cagri)

        #eğer ikisi de uygun olmazsa
        if asansor_1_skor == -1 and asansor_2_skor == -1:
            return None
        
        #uygunluk varsa en yüksek skoru olanı seçeceğiz
        if asansor_1_skor > asansor_2_skor:
            return self.asansor_1
        else:
            return self.asansor_2
        
    #asansör skorlaması (-1 uygun değil gerisinde en yüksek skoru olan daha iyi)
    def _asansor_skorla(self, asansor:Asansor, cagri:Cagri) -> int:
        skor = 100 #başta herkesin skoru yüz

        #asansör arızalı ise
        if asansor.durum == AsansorDurum.ARIZALI:
            return -1
        
        #mesafe faktörü(yakınsa daha iyi)
        mesafe = abs(asansor.mevcut_kat - cagri.cagri_kati)
        skor -= mesafe * 5

        #durum faktörü
        if asansor.durum == AsansorDurum.BOS:
            skor += 30
        elif asansor.durum == AsansorDurum.HAREKET_EDIYOR:
            if self._yon_uyumlu(asansor, cagri):
                skor += 15
            else:
                skor -= 25

        skor -= len(asansor.hedef_katlar)*3

        return skor

    #çağrı asansörün yönüyle uyumlu mu?
    def _yon_uyumlu(self, asansor:Asansor, cagri:Cagri) -> bool:

        if asansor.yon == cagri.yon:
            if cagri.yon == Yon.YUKARI and asansor.mevcut_kat <= cagri.cagri_kati:
                return True
            elif cagri.yon == Yon.ASAGI and asansor.mevcut_kat >= cagri.cagri_kati:
                return True
        return False
    
    #asansöre çağrıyı atayacağız
    def _cagri_ata(self, asansor:Asansor, cagri:Cagri):

        #eğer orda değilse çağrı katını hedeflere ekleyeceğiz
        if not asansor.mevcut_kat == cagri.cagri_kati:
            if cagri.cagri_kati not in asansor.hedef_katlar:
                asansor.hedef_katlar.append(cagri.cagri_kati)

        #hedefleri optimize edeceğiz
        self._hedef_sirala(asansor)

        #asansörü aktif edelim
        if asansor.durum == AsansorDurum.BOS:
            asansor.durum = AsansorDurum.HAREKET_EDIYOR

        #çağrıyı aktif listeye ekleyeceğiz
        cagri.durum = "atandı"
        self.aktif_cagrilar.append(cagri)

        self.log_ekle(f"Asansör {asansor.id} -> {cagri.cagri_kati}. kata gidiyor")

    #hedef katları SCAN algo ile sıralayacağız
    def _hedef_sirala(self, asansor:Asansor):

        if not asansor.hedef_katlar:
            asansor.yon = Yon.DURGUN
            return
        
        #hedefleri yukarı ve aşağı olarak ayır
        yukari_hedefler = [k for k in asansor.hedef_katlar if k > asansor.mevcut_kat]
        asagi_hedefler = [k for k in asansor.hedef_katlar if k < asansor.mevcut_kat]

        #bunları sırayalım
        yukari_hedefler.sort() #küçükten büyüğe
        asagi_hedefler.sort(reverse=True) #büyükten küçüğe

        #mevcut yöne öncelik vereceğiz
        if asansor.yon == Yon.YUKARI or asansor.yon == Yon.DURGUN:
            if yukari_hedefler:
                asansor.hedef_katlar = yukari_hedefler + asagi_hedefler
                asansor.yon = Yon.YUKARI
            else:
                asansor.hedef_katlar = asagi_hedefler
                asansor.yon = Yon.ASAGI if asagi_hedefler else Yon.DURGUN
        else:
            if asagi_hedefler:
                asansor.hedef_katlar = asagi_hedefler + yukari_hedefler
                asansor.yon = Yon.ASAGI
            else:
                asansor.hedef_katlar = yukari_hedefler
                asansor.yon = Yon.YUKARI if yukari_hedefler else Yon.DURGUN

    

    #döngüyü önlemek için sadece yeni log mesajları
    def _yeni_log_mesajlari(self) -> List[str]:
        yeni_mesajlar = self.log_mesajlari[self.son_log_sayisi:]
        self.son_log_sayisi = len(self.log_mesajlari)
        return yeni_mesajlar
    
    #asansör hareket simulasyon - her çağrıda çalışacak
    def _asansor_simulasyonu(self):
        simdiki_zaman = time.time()
        
        # 2 saniyede bir hareket et (gerçek zamanlı simülasyon)
        if simdiki_zaman - self.son_hareket_zamani < 2.0:
            return
            
        self.son_hareket_zamani = simdiki_zaman
        
        # Her asansörü hareket ettir
        self._asansor_hareket_et(self.asansor_1)
        self._asansor_hareket_et(self.asansor_2)
        
        # Bekleyen çağrıları kontrol et
        self._bekleyen_cagri_isle()


    #tek asansörü hareket ettirmek için
    def _asansor_hareket_et(self, asansor: Asansor):

        # Eğer hedef yoksa, boş duruma geç
        if not asansor.hedef_katlar:
            if asansor.durum != AsansorDurum.BOS:
                asansor.durum = AsansorDurum.BOS
                asansor.yon = Yon.DURGUN
                self.log_ekle(f"🛑 Asansör {asansor.id} durdu (hedef yok)")
            return
        
        hedef_kat = asansor.hedef_katlar[0]
        
        # Hedefe ulaştı mı?
        if asansor.mevcut_kat == hedef_kat:
            # Hedefi listeden çıkar
            asansor.hedef_katlar.pop(0)
            
            # Kapıyı aç
            asansor.durum = AsansorDurum.KAPI_ACIK
            asansor.kapi_acilma_zamani = time.time()
            
            self.log_ekle(f"🚪 Asansör {asansor.id} {hedef_kat}. katta - Kapı açık")
            
            # 3 saniye sonra kapı kapanacak (bir sonraki çağrıda)
            return
        
        # Kapı açıksa ve 3 saniye geçtiyse kapıyı kapat
        if asansor.durum == AsansorDurum.KAPI_ACIK:
            if time.time() - asansor.kapi_acilma_zamani > 3.0:
                asansor.durum = AsansorDurum.HAREKET_EDIYOR
                self.log_ekle(f"🚪 Asansör {asansor.id} kapı kapandı - Hareket başlıyor")
            return
        
        # Hareket et
        if hedef_kat > asansor.mevcut_kat:
            asansor.mevcut_kat += 1
            asansor.yon = Yon.YUKARI
            asansor.durum = AsansorDurum.HAREKET_EDIYOR
            self.log_ekle(f"⬆️ Asansör {asansor.id} → {asansor.mevcut_kat}. kat")
            
        elif hedef_kat < asansor.mevcut_kat:
            asansor.mevcut_kat -= 1
            asansor.yon = Yon.ASAGI
            asansor.durum = AsansorDurum.HAREKET_EDIYOR
            self.log_ekle(f"⬇️ Asansör {asansor.id} → {asansor.mevcut_kat}. kat")


    #bekleyen çağrıları kontrol eder, uygun asansöre atar
    def _bekleyen_cagri_isle(self):
        if not self.bekleyen_cagrilar:
            return
            
        atanan_cagrilar = []
        
        for cagri in self.bekleyen_cagrilar:
            secilen_asansor = self._asansor_sec(cagri)
            if secilen_asansor:
                self._cagri_ata(secilen_asansor, cagri)
                atanan_cagrilar.append(cagri)
                self.log_ekle(f"✅ Bekleyen çağrı atandı: Asansör {secilen_asansor.id}")
        
        # Atanan çağrıları bekleyenlerden çıkar
        for cagri in atanan_cagrilar:
            self.bekleyen_cagrilar.remove(cagri)


    #asansör içindeyken hedef kat ekler(kullanıcı tuşa basar), frontendden çağırılacak
    def hedef_kat_ekle(self, asansor_id: int, hedef_kat: int, yolcu_kilosu: float = 0) -> Dict:

        if not (-3 <= hedef_kat <= 12):
            return {'hata': 'Geçersiz kat numarası!'}
            
        if asansor_id not in [1, 2]:
            return {'hata': 'Geçersiz asansör ID!'}
        
        asansor = self.asansor_1 if asansor_id == 1 else self.asansor_2
        
        # Kapasite kontrolü
        if asansor.mevcut_yuk + yolcu_kilosu > 130:
            self.log_ekle(f"⚠️ Asansör {asansor_id} kapasite aştı! ({asansor.mevcut_yuk + yolcu_kilosu}kg)")
            return {'hata': f'Kapasite aşıldı! Maks: 130kg, Mevcut: {asansor.mevcut_yuk}kg'}
        
        # Ağırlık ekle
        asansor.mevcut_yuk += yolcu_kilosu
        
        # Hedef katı ekle
        if hedef_kat not in asansor.hedef_katlar and hedef_kat != asansor.mevcut_kat:
            asansor.hedef_katlar.append(hedef_kat)
            self._hedef_sirala(asansor)
            
            self.log_ekle(f"🎯 Asansör {asansor_id} yeni hedef: {hedef_kat}. kat (+{yolcu_kilosu}kg)")
            
            return {
                'durum': 'eklendi',
                'mesaj': f'Hedef {hedef_kat}. kat eklendi',
                'toplam_agirlik': asansor.mevcut_yuk
            }
        else:
            return {'mesaj': 'Hedef zaten mevcut veya aynı kattasınız'}


    #yolcu indirme işlemi yapılacak
    def yolcu_indi(self, asansor_id: int, inen_kilo: float) -> Dict:
        if asansor_id not in [1, 2]:
            return {'hata': 'Geçersiz asansör ID!'}
            
        asansor = self.asansor_1 if asansor_id == 1 else self.asansor_2
        
        if asansor.durum != AsansorDurum.KAPI_ACIK:
            return {'hata': 'Asansör kapısı açık değil!'}
            
        # Ağırlık düş
        asansor.mevcut_yuk = max(0, asansor.mevcut_yuk - inen_kilo)
        
        self.log_ekle(f"👋 Asansör {asansor_id} yolcu indi (-{inen_kilo}kg), Kalan: {asansor.mevcut_yuk}kg")
        
        return {
            'durum': 'indi',
            'kalan_agirlik': asansor.mevcut_yuk
        }




#test için basit bir kullanım
if __name__ == "__main__":
    sistem = AsansorSistemi()

    print("TEST BAŞLIYOR")

    #deneme 5.kattan yukarı çağıracağız
    sonuc1 = sistem.cagri_yap(5, "yukarı")
    print(f"Test 1 : {sonuc1}")

    #deneme 10.kattan aşağı çağıracağız
    sonuc2 = sistem.cagri_yap(10, "aşağı")
    print(f"Test 2 : {sonuc2}")

    #sistem durumunu göstereceğiz
    print(f"\n Sistem Durumu:")
    durum = sistem.sistem_durumu()
    print(f"Asansör 1: Kat {durum['asansor_1']['kat']}, Durum : {durum['asansor_1']['durum']}")
    print(f"Asansör 2: Kat {durum['asansor_2']['kat']}, Durum : {durum['asansor_2']['durum']}")