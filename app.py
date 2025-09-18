from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
from elevator_logic import AsansorSistemi
import threading
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'asansor_secret_key'
socketio = SocketIO(app)

#sistemi burda oluşturcaz (instance)
sistem = AsansorSistemi()

def asansor_sim_thread():
    while True:
        sistem._asansor_simulasyonu()
        time.sleep(2)

#test
@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({
        'message' : 'Flask başarılı',
        'asansor_sayisi' : 2,
        'kat_sayisi' : 16
    })

#sistem durum APIsi
@app.route('/api/durum')
def sistem_durumu():
    return jsonify(sistem.sistem_durumu())

#çağrı yapma APIsi
@app.route('/api/cagri/<int:kat>/<yon>')
def cagri_yap(kat, yon):
    sonuc = sistem.cagri_yap(kat, yon)
    return jsonify(sonuc)

# Asansör içi hedef kat ekleme API'si
@app.route('/api/hedef/<int:asansor_id>/<int:hedef_kat>')
def hedef_ekle(asansor_id, hedef_kat):
    # Kilo parametresi opsiyonel (query parameter)
    kilo = float(request.args.get('kilo', 0))
    sonuc = sistem.hedef_kat_ekle(asansor_id, hedef_kat, kilo)
    return jsonify(sonuc)

# Yolcu indirme API'si
@app.route('/api/indi/<int:asansor_id>')
def yolcu_indi(asansor_id):
    inen_kilo = float(request.args.get('kilo', 70))
    sonuc = sistem.yolcu_indi(asansor_id, inen_kilo)
    return jsonify(sonuc)



if __name__ == '__main__':
    print('Asansör sistemi başlatılıyor...')
    print("🌐 Tarayıcıda şu adresi açın: http://localhost:5000")
    threading.Thread(target = asansor_sim_thread, daemon=True).start()
    socketio.run(app, debug=True, port=5000)