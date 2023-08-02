def find_class_in_file(file_path, class_name):
    try:
        # Buka file Notepad
        with open(file_path, 'r') as file:
            # Baca seluruh konten file
            file_content = file.read()

            # Cari class tertentu di dalam konten file
            if class_name in file_content:
                print(f"Class '{class_name}' ditemukan di dalam file.")
            else:
                print(f"Class '{class_name}' tidak ditemukan di dalam file.")
    except FileNotFoundError:
        print("File tidak ditemukan.")

# Contoh penggunaan
file_path = 'path/to/your/notepad/file.txt'
class_name_to_find = 'NamaClassTertentu'
find_class_in_file(file_path, class_name_to_find)