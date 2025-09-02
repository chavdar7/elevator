import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AsansorDurum(Enum):
    BOS : "boş"
    HAREKET_EDIYOR : "hareket_ediyor"
    KAPI_ACIK : "kapı_açık"
    ARIZALI : "arızalı"

class Yon(Enum):
    YUKARI : "yukarı"
    ASAGI : "aşağı"
    DURGUN : "durgun"

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
    kapı_acılma_zamanı : float = 0.0

    def __post_init__(self):
        if self.hedef_katlar is None:
            self.hedef_katlar = []


#ana asansör sistemi
class AsansorSistemi:
    def __init__(self):
        self.asansor_1 = Asansor(id=1)
        self.asansor_2 = Asansor(id=2)
        self.bekleyen_cagrilar = List[Cagri] = []
        self.aktif_cagrilar = List[Cagri] = []
        self.log_mesajlari = List[str] = []

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
            'log_mesajlari' : self.log_mesajlari[-5:]
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
