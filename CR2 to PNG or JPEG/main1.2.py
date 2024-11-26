import os
import rawpy
import imageio
from tkinter import Tk, filedialog, Button, Label, StringVar, OptionMenu
from tkinter.ttk import Progressbar
import threading
import concurrent.futures

# Funksjon for å velge CR2-filer
def choose_files():
    file_paths = filedialog.askopenfilenames(title="Velg CR2-filer", filetypes=[("CR2 files", "*.cr2")])
    if file_paths:
        file_paths_label.set(f"Valgte filer: {len(file_paths)} filer valgt")
    else:
        file_paths_label.set("Ingen filer valgt")
    return root.tk.splitlist(file_paths)

# Funksjon for å velge utgangsmappen
def choose_output_folder():
    output_folder = filedialog.askdirectory(title="Velg utgangsmappen")
    if output_folder:
        output_folder_label.set(f"{output_folder}")
    else:
        output_folder_label.set("Ingen utgangsmappen valgt")
    return output_folder

# Funksjon for å konvertere CR2-filer til ønsket format (jpeg eller png)
def convert_cr2_to_format(file_path, output_folder, format='jpeg'):
    try:
        # Sjekk om formatet er gyldig
        if format not in ['jpeg', 'png']:
            raise ValueError("Format must be 'jpeg' eller 'png'")

        # Opprett utgangsmappen hvis den ikke eksisterer
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.{format}")

        # Les CR2-filen og konverter den til ønsket format
        with rawpy.imread(file_path) as raw:
            rgb = raw.postprocess()
            imageio.imwrite(output_path, rgb)
            print(f"Converted {file_name} to {format.upper()}")
        return file_path
    except Exception as e:
        print(f"Failed to convert {file_path}: {e}")
        return None

# Start konverteringen
def start_conversion():
    if not file_paths or not output_folder:
        progress_var.set("Velg filer og utgangsmappen først!")
        return

    format = format_var.get()
    progress_bar['maximum'] = len(file_paths)

    # Kjør konverteringen i en egen tråd
    def run_conversion():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(convert_cr2_to_format, file_path, output_folder, format) for file_path in file_paths]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if future.result():
                    progress_bar['value'] = i + 1
                    progress_var.set(f"Ferdig: {i + 1}/{len(file_paths)}")
                    root.update_idletasks()
        
        progress_var.set("Konvertering fullført!")

    threading.Thread(target=run_conversion).start()

# Sett filstiene
def set_file_paths():
    global file_paths
    file_paths = choose_files()

# Sett utgangsmappen
def set_output_folder():
    global output_folder
    output_folder = choose_output_folder()

root = Tk()
root.title("CR2 til PNG/JPEG Konverterer | Laget av Henrik S")
root.geometry("520x400")

# Brukergrensesnitt for å velge konverteringsformat
label = Label(root, text="Velg konverteringsformat:")
label.pack(pady=10)

format_var = StringVar(root)
format_var.set('png')

format_menu = OptionMenu(root, format_var, 'jpeg', 'png')
format_menu.pack(pady=5)

# Knapp for å velge filer
file_button = Button(root, text="Velg filer", command=set_file_paths)
file_button.pack(pady=5)

file_paths_label = StringVar()
file_paths_label.set("Ingen filer valgt")
file_paths_info = Label(root, textvariable=file_paths_label)
file_paths_info.pack(pady=5)

# Knapp for å velge utgangsmappen
output_folder_button = Button(root, text="Velg utgangsmappen", command=set_output_folder)
output_folder_button.pack(pady=5)

output_folder_label = StringVar()
output_folder_label.set("Ingen utgangsmappen valgt")
output_folder_info = Label(root, textvariable=output_folder_label)
output_folder_info.pack(pady=5)

# Knapp for å starte konvertering
start_button = Button(root, text="Start konvertering", command=start_conversion)
start_button.pack(pady=20)

# Fremdriftsindikator
progress_var = StringVar()
progress_bar = Progressbar(root, orient='horizontal', length=370, mode='determinate')
progress_bar.pack(pady=10)

progress_label = Label(root, textvariable=progress_var)
progress_label.pack(pady=5)

root.mainloop()
