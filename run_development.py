from livereload import Server
import subprocess
import sys
import atexit

# Jalankan server Flask dalam mode debug di proses terpisah
# Mode debug akan secara otomatis me-reload saat file .py berubah
flask_process = subprocess.Popen([sys.executable, "-m", "flask", "--app", "web_api:app", "run", "--host=0.0.0.0", "--port=5500", "--debug"])

# Daftarkan fungsi untuk memastikan proses Flask berhenti saat skrip utama keluar
atexit.register(flask_process.terminate)

# Buat server livereload yang hanya memantau file frontend
server = Server()
server.watch('*.html')
server.watch('*.js')

print("--- Development Live-Reload Server Started ---")
print("Buka http://127.0.0.1:5500 atau http://<IP_ANDA>:5500 di browser Anda.")
print("Server akan me-refresh browser secara otomatis saat Anda menyimpan perubahan.")
print("Tekan Ctrl+C untuk berhenti.")

# Gunakan port yang berbeda untuk livereload (misalnya 35729, default)
server.serve(liveport=35729)