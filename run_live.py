
import time
import subprocess
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AppRestartHandler(FileSystemEventHandler):
    def __init__(self, script_to_run):
        self.script_to_run = script_to_run
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process and self.process.poll() is None:
            print(f'>>> Terminating old `{self.script_to_run}` process...')
            self.process.terminate() # Coba terminate dulu
            try:
                self.process.wait(timeout=5) # Beri waktu 5 detik untuk berhenti
            except subprocess.TimeoutExpired:
                print(f'>>> Old `{self.script_to_run}` process did not terminate gracefully. Killing...')
                self.process.kill() # Jika tidak berhenti, paksa kill
                self.process.wait() # Tunggu sampai benar-benar mati
            time.sleep(0.5) # Beri jeda sebentar
        
        print(f'>>> Starting `{self.script_to_run}`...')
        self.process = subprocess.Popen([sys.executable, self.script_to_run])

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            print(f'>>> Change detected in `{os.path.basename(event.src_path)}`. Restarting application...')
            self.start_process()

if __name__ == "__main__":
    script_to_run = "main.py"
    path = "."

    event_handler = AppRestartHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    print("--- Live-Reload Server Started ---")
    print(f"Watching for changes in all .py files to restart `{script_to_run}`...")
    print("Press Ctrl+C to stop.")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("--- Live-Reload Server Stopped ---")
        observer.stop()
    finally:
        if event_handler.process and event_handler.process.poll() is None:
            print(f'>>> Terminating final `{event_handler.script_to_run}` process...')
            event_handler.process.terminate()
            try:
                event_handler.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f'>>> Final process did not terminate gracefully. Killing...')
                event_handler.process.kill()
                event_handler.process.wait()
        observer.join()
