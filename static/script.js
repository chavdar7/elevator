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

        // Aşağı butonu (-3. katta yok)
        if (kat > -3){
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


// Sistem durumunu yeniler
function refreshSystem() {
    fetch('/api/durum')
        .then(response => response.json())
        .then(data => {
            systemData = data;
            updateElevatorDisplays();
            updateSystemStatus();
            
            // Log mesajlarını güncelle
            if (data.log_mesajlari && data.log_mesajlari.length > 0) {
                data.log_mesajlari.forEach(msg => addLog(msg, false));
            }
        })
        .catch(error => {
            console.error("Sistem durumu hatası:", error);
            addLog(`Sistem durumu alınamadı: ${error.message}`);
        });
}

// Asansör görsellerini günceller
function updateElevatorDisplays() {
    if (!systemData) return;
    
    // Asansör 1
    updateSingleElevator('1', systemData.asansor_1);
    
    // Asansör 2  
    updateSingleElevator('2', systemData.asansor_2);
}


// Tek asansör görselini günceller
function updateSingleElevator(elevatorId, data) {
    // Kat
    document.getElementById(`elevator-${elevatorId}-floor`).textContent = data.kat;
    
    // Yön
    let yonSimge = '-';
    if (data.yon === 'yukarı') yonSimge = '↑';
    else if (data.yon === 'aşağı') yonSimge = '↓';
    document.getElementById(`elevator-${elevatorId}-direction`).textContent = yonSimge;
    
    // Ağırlık
    document.getElementById(`elevator-${elevatorId}-weight`).textContent = `${data.yuk} kg`;
    
    // Durum
    const statusElement = document.getElementById(`elevator-${elevatorId}-status`);
    statusElement.textContent = data.durum.charAt(0).toUpperCase() + data.durum.slice(1);
    
    // Durum rengini güncelle
    statusElement.className = 'status-info';
    if (data.durum === 'boş') {
        statusElement.style.background = '#c6f6d5';
        statusElement.style.color = '#22543d';
    } else if (data.durum === 'hareket_ediyor') {
        statusElement.style.background = '#ffd6cc';
        statusElement.style.color = '#9c4221';
    } else if (data.durum === 'kapı_açık') {
        statusElement.style.background = '#bee3f8';
        statusElement.style.color = '#1a365d';
    }
    
    // Hedefler
    const targetsElement = document.getElementById(`elevator-${elevatorId}-targets`);
    if (data.hedefler && data.hedefler.length > 0) {
        targetsElement.textContent = `Hedefler: ${data.hedefler.join(', ')}`;
    } else {
        targetsElement.textContent = 'Hedef yok';
    }
}

// Sistem durumu panelini günceller
function updateSystemStatus() {
    if (!systemData) return;
    
    // Bekleyen çağrı sayısı
    document.getElementById('waiting-calls').textContent = systemData.bekleyen_cagrilar || 0;
    
    // Sistem durumu
    document.getElementById('system-status').textContent = 'Aktif';
}

// Log mesajı ekler
function addLog(message, withTimestamp = true) {
    const logContainer = document.getElementById('log-container');
    const logItem = document.createElement('div');
    logItem.className = 'log-item';
    
    if (withTimestamp) {
        const now = new Date();
        const time = now.toLocaleTimeString('tr-TR');
        logItem.textContent = `[${time}] ${message}`;
    } else {
        logItem.textContent = message;
    }
    
    logContainer.appendChild(logItem);
    
    // En fazla 20 log tut
    while (logContainer.children.length > 20) {
        logContainer.removeChild(logContainer.firstChild);
    }
    
    // En alta scroll
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Otomatik yenileme başlatır
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(() => {
        refreshSystem();
    }, 3000); // 3 saniyede bir
    
    console.log("Otomatik yenileme başlatıldı (3s)");
}

// Otomatik yenilemeyi durdurur
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        console.log("Otomatik yenileme durduruldu");
    }
}

let currentElevatorId = null;

function openElevatorModal(elevatorId) {
    currentElevatorId = elevatorId;
    document.getElementById('elevator-modal').style.display = 'flex';
}

function closeElevatorModal() {
    document.getElementById('elevator-modal').style.display = 'none';
    currentElevatorId = null;
}

function submitElevatorTarget() {
    const hedefKat = document.getElementById('modal-target-floor').value;
    const kilo = document.getElementById('modal-weight').value;
    if (!hedefKat || !kilo || !currentElevatorId) {
        alert("Lütfen tüm alanları doldurun.");
        return;
    }
    fetch(`/api/hedef/${currentElevatorId}/${hedefKat}?kilo=${kilo}`)
        .then(response => response.json())
        .then(data => {
            addLog(data.mesaj || JSON.stringify(data));
            refreshSystem();
        })
        .catch(err => alert("Hata: " + err))
        .finally(() => closeElevatorModal());
}


let currentIndirElevatorId = null;

function openIndirModal(elevatorId) {
    currentIndirElevatorId = elevatorId;
    document.getElementById('indir-modal').style.display = 'flex';
}

function closeIndirModal() {
    document.getElementById('indir-modal').style.display = 'none';
    currentIndirElevatorId = null;
}

function submitIndir() {
    const kilo = document.getElementById('indir-weight').value;
    if (!kilo || !currentIndirElevatorId) {
        alert("Lütfen kilo girin.");
        return;
    }
    fetch(`/api/indi/${currentIndirElevatorId}?kilo=${kilo}`)
        .then(response => response.json())
        .then(data => {
            addLog(data.mesaj || JSON.stringify(data));
            refreshSystem();
        })
        .catch(err => alert("Hata: " + err))
        .finally(() => closeIndirModal());
}


// Test fonksiyonu
function testFlask() {
    console.log("Flask bağlantısı test ediliyor...");
    
    fetch('/test')
        .then(response => response.json())
        .then(data => {
            console.log("Flask test başarılı:", data);
            addLog(`Flask test başarılı: ${data.mesaj}`);
            
            // Başarı mesajını geçici olarak göster
            const testResult = document.getElementById('test-result');
            testResult.style.display = 'block';
            testResult.className = 'success';
            testResult.innerHTML = `
                <strong>Flask Bağlantısı OK!</strong><br>
                ${data.mesaj}<br>
                ${data.asansor_sayisi} asansör, ${data.kat_sayisi} kat
            `;
            
            setTimeout(() => {
                testResult.style.display = 'none';
            }, 3000);
        })
        .catch(error => {
            console.error("Flask test hatası:", error);
            addLog(`Flask test hatası: ${error.message}`);
        });
}


// Sayfa kapatılırken otomatik yenilemeyi durdur
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});