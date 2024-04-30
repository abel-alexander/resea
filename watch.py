import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class Watcher:
    DIRECTORY_TO_WATCH = "/path/to/your/directory"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take action when a file is created.
            print(f"Received created event - {event.src_path}.")
            # Run Alteryx workflow
            workflow_path = "/path/to/your/alteryx_workflow.yxmd"
            subprocess.run(['AlteryxEngineCmd.exe', workflow_path, event.src_path])
            # Delete the file
            os.remove(event.src_path)
            print(f"File {event.src_path} deleted after processing.")

if __name__ == '__main__':
    w = Watcher()
    w.run()
