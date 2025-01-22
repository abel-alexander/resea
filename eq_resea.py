import os
import hashlib
import subprocess
from datetime import datetime

# Path to the repository and the file to monitor
repo_dir = "/path/to/your/repo"
file_to_watch = os.path.join(repo_dir, "usage_logs.txt")
hash_file = os.path.join(repo_dir, ".last_hash")  # To store the last hash

def calculate_file_hash(filepath):
    """Calculate the SHA256 hash of a file."""
    with open(filepath, "rb") as f:
        file_data = f.read()
    return hashlib.sha256(file_data).hexdigest()

def load_last_hash(hash_file_path):
    """Load the last saved hash from the hash file."""
    if os.path.exists(hash_file_path):
        with open(hash_file_path, "r") as f:
            return f.read().strip()
    return None

def save_current_hash(hash_file_path, file_hash):
    """Save the current file hash to the hash file."""
    with open(hash_file_path, "w") as f:
        f.write(file_hash)

def main():
    os.chdir(repo_dir)

    # Calculate the current hash of the file
    if not os.path.exists(file_to_watch):
        print(f"Error: {file_to_watch} does not exist.")
        return

    current_hash = calculate_file_hash(file_to_watch)
    last_hash = load_last_hash(hash_file)

    # Check if the file has changed
    if current_hash != last_hash:
        print("File has changed. Committing and pushing...")
        try:
            # Add the file to staging
            subprocess.run(["git", "add", file_to_watch], check=True)

            # Commit the changes
            commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push the changes
            subprocess.run(["git", "push"], check=True)

            # Save the new hash
            save_current_hash(hash_file, current_hash)

            print("Changes committed and pushed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during commit/push: {e}")
    else:
        print("No changes detected. Nothing to commit.")

if __name__ == "__main__":
    main()
