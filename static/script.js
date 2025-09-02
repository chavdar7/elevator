//global değişkenler
let systemData = null;
let refreshInterval = null;

//sayfa yüklendiğinde çalışacak
document.addEventListener('DOMContentLoaded', function() {
    console.log("Asansör Sistemi UI yüklendi");

    //kat butonları
    createFloorButtons();
    
    //sistem durumu
    refreshSystem();

    //otomatik yenileme başlar(3s)
    startAutoRefresh();

    addLog("Asansör Sistemi Kullanıma Hazır");
})

//kat butonlarını oluştur
function createFloorButtons(){
    const floorsGrid = document.getElementById('floors-grid');

    //yukardan aşağıya katlar
    for (let kat = 12; kat >= -3; kat--){
        const floorRow = document.createElement('div');
        floorRow.className = 'floor-row';

        //kat no
        const floorNumber = document.createElement('div');
        floorNumber.className = 'floor-number';
        floorNumber.textContent = `KAT ${kat}`;

        //button container
        const floorButtons = document.createElement('div');
        floorButtons.className = 'floor-buttons';

        //yukarı butonu(12.katta olmayacak)
        if (kat<12){
            const upBtn = document.createElement('button');
            upBtn.className = 'floor-btn up';
            upBtn.textContent = '↑';
            upBtn.onclick = () => callElevator(kat, 'yukarı');
            upBtn.title = `${kat}. kattan yukarı`;
            floorButtons.appendChild(upBtn);
        }

        // Aşağı butonu (1. katta yok)
        if (kat > 1){
            const downBtn = document.createElement('button');
            downBtn.className = 'floor-btn down';
            downBtn.textContent = '↓';
            downBtn.onclick = () => callElevator(kat, 'aşağı');
            downBtn.title = `${kat}. kattan aşağı`;
            floorButtons.appendChild(downBtn);
        }

        // Elemanları birleştir
        floorRow.appendChild(floorNumber);
        floorRow.appendChild(floorButtons);
        floorsGrid.appendChild(floorRow);

    }
}

//asansör çağrısı yapar
function callElevator(kat, yon){
    console.log(`${kat}. kattan ${yon} çağrısı yapılıyor`);

    // Butonu geçici olarak devre dışı bırak
    const buttons = document.querySelectorAll(`button[onclick="callElevator(${kat}, '${yon}')"]`);
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.textContent = 'wait';
    });

    // API'ye istek gönder
    fetch(`/api/cagri/${kat}/${yon}`)
        .then(response => response.json())
        .then(data => {
            console.log("Asansör çağrı cevabı:", data);
            
            if (data.durum === 'atandi') {
                addLog(`${data.mesaj} (${kat}. kat ${yon})`);
            } else if (data.durum === 'beklemede') {
                addLog(`${data.mesaj} (${kat}. kat ${yon})`);
            } else if (data.hata) {
                addLog(`Hata: ${data.hata}`);
            }
            
            // Sistem durumunu yenile
            refreshSystem();
        })
        .catch(error => {
            console.error("Çağrı hatası:", error);
            addLog(`Bağlantı hatası: ${error.message}`);
        })
        .finally(() => {
            // Butonları tekrar aktif et (2 saniye sonra)
            setTimeout(() => {
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.textContent = yon === 'yukarı' ? '↑' : '↓';
                });
            }, 2000);
        });
}






/*
// Test fonksiyonu - Flask bağlantısını kontrol eder
function testFlask(){
    console.log("flask bağlantısı test ediliyor...");

    //test butonunu devre dışı bırak
    const button = document.querySelector('button');
    button.disabled = true;
    button.innerText = "Test ediliyor..." 

    //flask API ye istek gönder
    fetch('/test')
        .then(response => {
            if (response.ok){
                return response.json();
            }
            throw new Error("Network hatası")
        })
        .then(data => {
            console.log("Flaskdan gelen veri", data);
            showTestResult(true, data);
        })
        .catch(error => {
            console.error("hata", error);
            showTestResult(false, error.message);
        })
        .finally(() => {
            button.disabled = false;
            button.innerText = "Flask bağlantısını test et";
        })
}

//test sonucunu ekranda göster
function showTestResult(success, data){
    const resultDiv = document.getElementById('test-result');

    if (success){
        resultDiv.className = 'success';
        resultDiv.innerHTML = `
            <strong>Test Başarılı:</strong>
            <br>
            Mesaj: ${data.message}
            <br>
            Asansör Sayısı : ${data.asansor_sayisi}
            <br>
            Kat Sayısı : ${data.kat_sayisi}
        `;
    } else {
        resultDiv.className = 'error';
        resultDiv.innerHTML = `
            <strong>Hata</strong>
            <br>
            Hata Mesajı: ${data}
        `;
    }
}

// Sayfa yüklendiğinde çalışacak kod
document.addEventListener('DOMContentLoaded', function(){
    console.log("Asansör sistemi yüklendi.");
})
*/