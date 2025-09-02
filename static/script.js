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