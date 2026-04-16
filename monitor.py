import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_PATH = "./sensitive_files"
WEBHOOK_URL = "http://127.0.0.1:8000/alerts/webhook/"


class FIMHandler(FileSystemEventHandler):
    def send_alert(self, event_type, file_path):
        if "___jb_" in file_path or file_path.endswith('~') or file_path.endswith('.tmp'):
            return

        if event_type == "DELETED" and os.path.exists(file_path):
            return

        content = ""
        if event_type in ["CREATED", "MODIFIED"]:
            try:
                time.sleep(0.1)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read(2000)
            except Exception as e:
                content = f"[Unreadable: {str(e)}]"

        payload = {
            "file_path": file_path,
            "message": f"Action Detected: {event_type}",
            "content": content
        }

        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code == 201:
                print(f"[✅] Alert Sent: {event_type} -> {os.path.basename(file_path)}")
            else:
                print(f"[❌] Webhook Error: {response.status_code}")
        except Exception as e:
            print(f"[⚠️] Connection Error: Is Django running? ({e})")

    def on_modified(self, event):
        if not event.is_directory: self.send_alert("MODIFIED", event.src_path)

    def on_created(self, event):
        if not event.is_directory: self.send_alert("CREATED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory: self.send_alert("DELETED", event.src_path)


if __name__ == "__main__":
    if not os.path.exists(WATCH_PATH):
        os.makedirs(WATCH_PATH)

    event_handler = FIMHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=False)

    print(f"🛡️  FIM AGENT ACTIVE")
    print(f"[*] Monitoring: {os.path.abspath(WATCH_PATH)}")
    print(f"[*] Sending alerts to: {WEBHOOK_URL}")
    print("[*] Press Ctrl+C to stop.")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping FIM Agent...")
        observer.stop()
    observer.join()