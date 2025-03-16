import requests
from flask import Flask, render_template, jsonify
import threading
import time
from googletrans import Translator

app = Flask(__name__)

NEWS_API_KEY = '0f66b078be894fa5a7e7f150d20a85f0'  # Ganti dengan API Key Anda
TRANSLATOR = Translator()  # Inisialisasi translator

# Fungsi untuk Menerjemahkan Teks ke Bahasa Indonesia
def translate_to_indonesian(text):
    try:
        translated = TRANSLATOR.translate(text, src='auto', dest='id')
        return translated.text
    except Exception as e:
        print("Terjadi kesalahan dalam penerjemahan:", e)
        return text  # Jika gagal, kembalikan teks asli

# Variabel Global untuk Cache Data
bitcoin_data = {
    "harga": "Mengambil data...",
    "terendah": "Mengambil data...",
    "beli": "Mengambil data...",
    "jual": "Mengambil data..."
}

news_data = []

# Fungsi untuk Mengambil Data Bitcoin Secara Asinkron
def update_bitcoin_data():
    global bitcoin_data
    while True:
        try:
            url = "https://indodax.com/api/ticker/btcidr"
            response = requests.get(url).json()

            harga_terkini = response['ticker']['last']
            harga_terendah = response['ticker']['low']

            rekomendasi_beli = float(harga_terkini) * 0.98  # Simulasi beli
            rekomendasi_jual = float(harga_terkini) * 1.02  # Simulasi jual

            bitcoin_data = {
                "harga": harga_terkini,
                "terendah": harga_terendah,
                "beli": rekomendasi_beli,
                "jual": rekomendasi_jual
            }
        except Exception as e:
            print("Error:", e)

        time.sleep(3)  # Update setiap 3 detik

# Fungsi untuk Mengambil Berita Bitcoin
def update_news():
    global news_data
    while True:
        try:
            url = f"https://newsapi.org/v2/everything?q=bitcoin&apiKey=0f66b078be894fa5a7e7f150d20a85f0"
            response = requests.get(url).json()

            articles = response['articles']
            news_data = []
            for article in articles:
                title = article['title']
                description = article['description']
                # Menerjemahkan judul dan deskripsi ke Bahasa Indonesia
                translated_title = translate_to_indonesian(title)
                translated_description = translate_to_indonesian(description)
                news_data.append({
                    "title": translated_title,
                    "description": translated_description,
                    "url": article['url']
                })
        except Exception as e:
            print("Error fetching news:", e)

        time.sleep(600)  # Update berita setiap 10 menit

# Jalankan Update Data di Threading
threading.Thread(target=update_bitcoin_data, daemon=True).start()
threading.Thread(target=update_news, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(bitcoin_data)

@app.route('/news')
def get_news():
    return jsonify(news_data)

if __name__ == '__main__':
    app.run(debug=True)
