import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

# Define the file to watch and the repo directory
repo_dir = "/path/to/your/repo"
file_to_watch = os.path.join(repo_dir, "usage_logs.txt")

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == file_to_watch:
            print(f"Detected changes in {file_to_watch}. Committing and pushing...")
            try:
                # Change to the repo directory
                os.chdir(repo_dir)
                
                # Add the file to staging
                subprocess.run(["git", "add", file_to_watch], check=True)

                # Commit the changes
                commit_message = "Auto-commit: Detected changes in usage_logs.txt"
                subprocess.run(["git", "commit", "-m", commit_message], check=True)

                # Push the changes
                subprocess.run(["git", "push"], check=True)

                print("Changes committed and pushed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error during commit/push: {e}")

if __name__ == "__main__":
    # Set up the observer
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=repo_dir, recursive=False)

    print(f"Watching for changes in {file_to_watch}...")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
