from web_api import run_flask_app
import time

if __name__ == '__main__':
    print("Starting Flask web server...")
    print("You can access the web interface at http://<YOUR_LAPTOP_IP>:5001")
    print("--> Note: Ganti <YOUR_LAPTOP_IP> dengan alamat IP laptop Anda di jaringan WiFi.")
    print("Press Ctrl+C to stop the server.")
    
    # Menjalankan server Flask
    run_flask_app()