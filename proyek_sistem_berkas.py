from pathlib import Path
import shutil
import hashlib
import json

# =================================
# 1. PENGATURAN FOLDER
# =================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"
LOG_FILE = BASE_DIR / "aktivitas.log"

CATEGORIES = [
    "PUBLIC",
    "DATA_ANGGOTA",
    "DATA_RAHASIA"
]

# =================================
# 2. STATUS PROGRAM
# =================================

mounted = False
active_role = None

# =================================
# 3. HAK AKSES PENGGUNA
# =================================

PERMISSIONS = {
    "owner": {
        "PUBLIC": {"read": True, "write": True},
        "DATA_ANGGOTA": {"read": True, "write": True},
        "DATA_RAHASIA": {"read": True, "write": True}
    },

    "anggota": {
        "PUBLIC": {"read": True, "write": False},
        "DATA_ANGGOTA": {"read": True, "write": True},
        "DATA_RAHASIA": {"read": False, "write": False}
    },

    "tamu": {
        "PUBLIC": {"read": True, "write": False},
        "DATA_ANGGOTA": {"read": False, "write": False},
        "DATA_RAHASIA": {"read": False, "write": False}
    }
}

# =================================
# 4. MEMBUAT STRUKTUR FOLDER
# =================================
def log_activity(activity):

    from datetime import datetime

    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{waktu}] {activity}\n")

def initialize_project():

    DATA_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

    for category in CATEGORIES:
        folder = DATA_DIR / category
        folder.mkdir(exist_ok=True)

    print("Struktur folder berhasil dibuat!")


# =================================
# 5. LOGIN PENGGUNA
# =================================

def login():

    global active_role

    if active_role is not None:
        print("Anda masih login. Silakan Logout terlebih dahulu!")
        return

    print("\n===== LOGIN PENGGUNA =====")
    print("----------------------------")
    print("1. Owner")
    print("2. Anggota")
    print("3. Tamu")
    print("----------------------------")

    pilihan = input("Pilih peran: ")

    if pilihan == "1":
        active_role = "owner"

    elif pilihan == "2":
        active_role = "anggota"

    elif pilihan == "3":
        active_role = "tamu"

    else:
        print("Pilihan tidak valid!")
        return

    print("Login berhasil sebagai", active_role.upper())
    log_activity(f"Login sebagai {active_role.upper()}")

# =================================
# LOGOUT PENGGUNA
# =================================

def logout():
    global active_role, mounted

    if active_role is None:
        print("Belum ada pengguna yang login!")
        return

    log_activity(f"Logout dari akun {active_role.upper()}")

    active_role = None
    mounted = False

    print("Logout berhasil!")
    print("Akses folder telah ditutup.")

# =================================
# 6. MOUNT DAN UNMOUNT
# =================================

def mount_folder():
    global mounted

    if active_role is None:
        print("Silakan login terlebih dahulu!")
        return

    if mounted:
        print("Folder sudah di-mount!")
    else:
        mounted = True
        print("Mount berhasil!")
        print("Folder siap digunakan.")
        log_activity("Folder berhasil di-mount")

def unmount_folder():
    global mounted

    if active_role is None:
        print("Silakan login terlebih dahulu!")
        return

    if not mounted:
        print("Folder belum di-mount!")
    else:
        mounted = False
        print("Unmount berhasil!")
        print("Akses folder ditutup.")
        log_activity("Folder berhasil di-unmount")

# =================================
# 6. PEMERIKSAAN MOUNT
# =================================

def check_mount():

    if not mounted:
        print("Akses ditolak: folder belum di-mount!")
        return False

    return True

# =================================
# 7. PEMERIKSAAN HAK AKSES
# =================================

def check_permission(action, category):

    if active_role is None:
        print("Silakan login terlebih dahulu!")
        return False

    izin = PERMISSIONS[active_role][category][action]

    if izin:
        return True
    else:
        print("Akses ditolak!")
        return False

# =================================
# 8. PENGELOLAAN FILE TXT
# =================================

# Menampilkan daftar file
def list_files():

    if not check_mount():
        return

    category = input("Pilih kategori: ").upper()

    if category not in CATEGORIES:
        print("Kategori tidak valid!")
        return

    if not check_permission("read", category):
        return

    folder = DATA_DIR / category
    files = list(folder.glob("*.txt"))

    print("\n=== DAFTAR FILE ===")

    if not files:
        print("Belum ada file TXT.")
    else:
        for file in files:
            print("-", file.name)

# Membaca isi file
def read_file():

    if not check_mount():
        return

    category = input("Pilih kategori: ").upper()

    if category not in CATEGORIES:
        print("Kategori tidak valid!")
        return

    if not check_permission("read", category):
        return

    filename = input("Nama file: ")

    if Path(filename).name != filename or not filename.endswith(".txt"):
        print("Nama file tidak valid!")
        return

    file_path = DATA_DIR / category / filename

    if file_path.exists():
        print("\n=== ISI FILE ===")
        print(file_path.read_text(encoding="utf-8"))
    else:
        print("File tidak ditemukan!")

# Membuat atau mengubah file
def write_file():

    if not check_mount():
        return

    category = input("Pilih kategori: ").upper()

    if category not in CATEGORIES:
        print("Kategori tidak valid!")
        return

    if not check_permission("write", category):
        return

    filename = input("Nama file (.txt): ")

    if Path(filename).name != filename or not filename.endswith(".txt"):
        print("Nama file tidak valid!")
        return

    content = input("Masukkan isi file: ")

    file_path = DATA_DIR / category / filename

    file_path.write_text(content, encoding="utf-8")

    print("File berhasil disimpan!")
    log_activity(f"File {filename} dibuat atau diubah di {category}")

# Menghapus file
def delete_file():

    if not check_mount():
        return

    category = input("Pilih kategori: ").upper()

    if category not in CATEGORIES:
        print("Kategori tidak valid!")
        return

    if not check_permission("write", category):
        return

    filename = input("Nama file yang ingin dihapus: ")

    if Path(filename).name != filename or not filename.endswith(".txt"):
        print("Nama file tidak valid!")
        return

    file_path = DATA_DIR / category / filename

    if file_path.exists():
        file_path.unlink()
        print("File berhasil dihapus!")
        log_activity(f"File {filename} dihapus dari {category}")
    else:
        print("File tidak ditemukan!")

# Backup file
def backup_file():

    if not check_mount():
        return

    category = input("Pilih kategori: ").upper()

    if category not in CATEGORIES:
        print("Kategori tidak valid!")
        return

    if not check_permission("read", category):
        return

    filename = input("Nama file yang ingin di-backup: ")

    if Path(filename).name != filename or not filename.endswith(".txt"):
        print("Nama file tidak valid!")
        return

    file_path = DATA_DIR / category / filename

    if not file_path.exists():
        print("File tidak ditemukan!")
        return

    backup_category = BACKUP_DIR / category
    backup_category.mkdir(exist_ok=True)

    backup_path = backup_category / filename

    if backup_path.exists():
        konfirmasi = input(
            "File backup sudah ada. Timpa file? (y/n): "
        ).lower()

        if konfirmasi != "y":
            print("Backup dibatalkan!")
            return

    shutil.copy2(file_path, backup_path)

    print("Backup berhasil!")
    print("File tersimpan di folder backup.")
    log_activity(f"File {filename} di-backup dari {category}")



# Full Backup
def full_backup():

    if active_role is None:
        print("Silakan login terlebih dahulu!")
        return

    if active_role != "owner":
        print("Akses ditolak! Full Backup hanya untuk Owner.")
        return

    if not check_mount():
        return

    from datetime import datetime

    waktu = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    full_backup_dir = BACKUP_DIR / "full_backup"
    destination = full_backup_dir / waktu

    try:
        full_backup_dir.mkdir(parents=True, exist_ok=True)

        # Menyalin seluruh folder data
        shutil.copytree(DATA_DIR, destination)

        # Membuat manifest SHA-256
        manifest = {}

        for file in DATA_DIR.rglob("*"):
            if file.is_file():
                relative = file.relative_to(DATA_DIR).as_posix()

                sha = hashlib.sha256(file.read_bytes()).hexdigest()
                manifest[relative] = sha

        # Menyimpan manifest di dalam folder backup
        manifest_path = destination / "_manifest.json"

        manifest_path.write_text(
            json.dumps(manifest, indent=4),
            encoding="utf-8"
        )

        print("\nFull Backup berhasil!")
        print("Nama Backup :", waktu)
        print("Jumlah File :", len(manifest))

        log_activity(
            "Full Backup berhasil dilakukan oleh Owner"
        )

    except Exception as e:
        print("Full Backup gagal:", e)


# Restore Full Backup
def restore_file():

    if active_role is None:
        print("Silakan login terlebih dahulu!")
        return

    if active_role != "owner":
        print("Akses ditolak! Restore hanya untuk Owner.")
        return

    if not check_mount():
        return

    full_backup_dir = BACKUP_DIR / "full_backup"

    if not full_backup_dir.exists():
        print("Folder Full Backup tidak ditemukan!")
        return

    # Mengambil daftar backup yang tersedia
    backups = sorted(
        [
            folder for folder in full_backup_dir.iterdir()
            if folder.is_dir()
            and (folder / "_manifest.json").is_file()
        ],
        key=lambda folder: folder.name,
        reverse=True
    )

    if not backups:
        print("Belum ada Full Backup!")
        return

    print("\n===== DAFTAR FULL BACKUP =====")

    for i, folder in enumerate(backups, start=1):
        print(f"[{i}] {folder.name}")

    pilihan = input("Pilih backup yang ingin di-restore: ")

    if not pilihan.isdigit():
        print("Pilihan tidak valid!")
        return

    nomor = int(pilihan)

    if nomor < 1 or nomor > len(backups):
        print("Pilihan tidak tersedia!")
        return

    backup_terpilih = backups[nomor - 1]

    manifest_path = backup_terpilih / "_manifest.json"

    # Membaca manifest
    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as e:
        print("Manifest backup tidak dapat dibaca:", e)
        return

    print("\nPERINGATAN!")
    print("Restore akan mengganti seluruh isi folder DATA.")

    konfirmasi = input("Lanjutkan Restore? (y/n): ").lower()

    if konfirmasi != "y":
        print("Restore dibatalkan!")
        return

    # Membuat folder sementara
    temp_dir = BASE_DIR / "data_restore_temp"
    old_dir = BASE_DIR / "data_sebelum_restore"

    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        if old_dir.exists():
            shutil.rmtree(old_dir)

        # Menyalin backup ke folder sementara
        shutil.copytree(
            backup_terpilih,
            temp_dir,
            ignore=shutil.ignore_patterns("_manifest.json")
        )

        # Verifikasi SHA-256
        hasil = {}

        for file in temp_dir.rglob("*"):
            if file.is_file():
                relative = file.relative_to(temp_dir).as_posix()

                sha = hashlib.sha256(file.read_bytes()).hexdigest()
                hasil[relative] = sha

        if hasil != manifest:
            shutil.rmtree(temp_dir)
            print("Verifikasi SHA-256 gagal!")
            print("Data lama tidak diubah.")
            return

        # Mengganti folder DATA dengan hasil backup
        if DATA_DIR.exists():
            DATA_DIR.rename(old_dir)

        try:
            temp_dir.rename(DATA_DIR)

        except Exception:
            if old_dir.exists() and not DATA_DIR.exists():
                old_dir.rename(DATA_DIR)
            raise

        # Menghapus data lama setelah restore berhasil
        if old_dir.exists():
            shutil.rmtree(old_dir)

        print("\nRestore berhasil!")
        print("Backup       :", backup_terpilih.name)
        print("Jumlah File  :", len(manifest))
        print("SHA-256      : SESUAI")

        log_activity(
            f"Full Restore berhasil dari {backup_terpilih.name}"
        )

    except Exception as e:
        print("Restore gagal:", e)

        if temp_dir.exists():
            shutil.rmtree(temp_dir)


# =================================
# 9. MENU UTAMA
# =================================

def main():

    initialize_project()

    while True:

        print("\n========================================")
        print("             SISTEM BERKAS")
        print("========================================")

        # Menampilkan status login
        if active_role is None:
            print("Status Login  : BELUM LOGIN")
        else:
            print("Status Login  :", active_role.upper())

        # Menampilkan status folder
        if mounted:
            print("Status Folder : MOUNTED")
        else:
            print("Status Folder : UNMOUNTED")

        print("----------------------------------------")
        print("[1] Login          [6] Baca File")
        print("[2] Mount          [7] Buat/Ubah File")
        print("[3] Unmount        [8] Hapus File")
        print("[4] Cek Status     [9] Backup")
        print("[5] Daftar File    [10] Full Backup")
        print("[11] Restore       [12] Logout")
        print("[0] Keluar")
        print("----------------------------------------")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            login()

        elif pilihan == "2":
            mount_folder()

        elif pilihan == "3":
            unmount_folder()

        elif pilihan == "4":
            if mounted:
                print("Status: MOUNTED")
            else:
                print("Status: UNMOUNTED")

        elif pilihan == "5":
            list_files()

        elif pilihan == "6":
            read_file()

        elif pilihan == "7":
            write_file()

        elif pilihan == "8":
            delete_file()

        elif pilihan == "9":
            backup_file()

        elif pilihan == "10":
            full_backup()

        elif pilihan == "11":
            restore_file()

        elif pilihan == "12":
            logout()

        elif pilihan == "0":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()