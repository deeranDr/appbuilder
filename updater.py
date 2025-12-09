# updater.py
import os, sys, time, shutil, subprocess

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]
    time.sleep(2)  # give app time to close
    try:
        shutil.copy2(new_path, old_path)
    except Exception as e:
        print("Update failed:", e)
        sys.exit(1)

    os.remove(new_path)
    subprocess.Popen([old_path])
    sys.exit(0)

if __name__ == "__main__":
    main()
