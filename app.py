from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
from elevator_logic import AsansorSistemi

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asansor_secret_key'
socketio = SocketIO(app)

#sistemi burda oluşturcaz (instance)
sistem = AsansorSistemi()

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


if __name__ == '__main__':
    print('Asansör sistemi başlatılıyor...')
    print("🌐 Tarayıcıda şu adresi açın: http://localhost:5000")
    socketio.run(app, debug=True, port=5000)