import os
import rawpy
import imageio
from tkinter import Tk, filedialog, Button, Label, StringVar, OptionMenu
from tkinter.ttk import Progressbar
import threading

# Funksjon for å velge filer
def choose_files():
    # Åpner en filvelger dialog for å velge CR2 filer
    file_paths = filedialog.askopenfilenames(title="Velg CR2-filer", filetypes=[("CR2 files", "*.cr2")])
    if file_paths:
        # Oppdaterer label med antall valgte filer
        file_paths_label.set(f"Valgte filer: {len(file_paths)} filer valgt")
    else:
        # Oppdaterer label hvis ingen filer er valgt
        file_paths_label.set("Ingen filer valgt")
    # Returnerer filbaner som en liste
    return root.tk.splitlist(file_paths)

# Funksjon for å velge utgangsmappen
def choose_output_folder():
    # Åpner en dialog for å velge utgangsmappen
    output_folder = filedialog.askdirectory(title="Velg utgangsmappen")
    if output_folder:
        # Oppdaterer label med valgt utgangsmappe
        output_folder_label.set(f"{output_folder}")
    else:
        # Oppdaterer label hvis ingen utgangsmappe er valgt
        output_folder_label.set("Ingen utgangsmappen valgt")
    # Returnerer utgangsmappen som en streng
    return output_folder

# Funksjon for å konvertere CR2-filer til valgt format
def convert_cr2_to_format(file_paths, output_folder, format='jpeg'):
    # Sjekker om formatet er gyldig
    if format not in ['jpeg', 'png']:
        raise ValueError("Format must be 'jpeg' eller 'png'")

    # Oppretter utgangsmappen hvis den ikke eksisterer
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Setter maksimalverdien for progressbaren
    progress_bar['maximum'] = len(file_paths)
    for i, file_path in enumerate(file_paths):
        file_name = os.path.basename(file_path)  # Henter filnavnet
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.{format}")  # Definerer utgangsbanen

        # Leser CR2-filen og konverterer den til RGB
        with rawpy.imread(file_path) as raw:
            rgb = raw.postprocess()  # Postprosessering av råbildet
            imageio.imwrite(output_path, rgb)  # Skriver den konverterte filen til utgangsbanen
            print(f"Converted {file_name} to {format.upper()}")  # Skriver ut en melding om konvertering

        # Oppdaterer progressbaren og statuslabel
        progress_bar['value'] = i + 1
        progress_var.set(f"Ferdig: {i + 1}/{len(file_paths)}")
        root.update_idletasks()  # Oppdaterer GUI

    # Setter sluttstatus når konverteringen er fullført
    progress_var.set("Konvertering fullført!")

# Funksjon som starter konverteringsprosessen i en egen tråd
def start_conversion():
    if not file_paths or not output_folder:
        # Oppdaterer status hvis filer eller utgangsmappe ikke er valgt
        progress_var.set("Velg filer og utgangsmappen først!")
        return

    format = format_var.get()  # Henter valgt format
    # Starter konverteringsprosessen i en ny tråd for å unngå å blokkere GUI
    threading.Thread(target=convert_cr2_to_format, args=(file_paths, output_folder, format)).start()

# Funksjon som setter filbanene valgt av brukeren
def set_file_paths():
    global file_paths
    file_paths = choose_files()

# Funksjon som setter utgangsmappen valgt av brukeren
def set_output_folder():
    global output_folder
    output_folder = choose_output_folder()

# Oppretter hovedvinduet for GUI
root = Tk()
root.title("CR2 til PNG/JPEG Konverterer | Laget av Henrik S")
root.geometry("520x400")  # Setter størrelsen på vinduet til 520x400 piksler

# Label og meny for å velge konverteringsformat
label = Label(root, text="Velg konverteringsformat:")
label.pack(pady=10)

format_var = StringVar(root)
format_var.set('png')  # Setter standardformatet til 'png'

format_menu = OptionMenu(root, format_var, 'jpeg', 'png')
format_menu.pack(pady=5)

# Knapp for å velge filer
file_button = Button(root, text="Velg filer", command=set_file_paths)
file_button.pack(pady=5)

# Label for å vise valgte filer
file_paths_label = StringVar()
file_paths_label.set("Ingen filer valgt")
file_paths_info = Label(root, textvariable=file_paths_label)
file_paths_info.pack(pady=5)

# Knapp for å velge utgangsmappen
output_folder_button = Button(root, text="Velg utgangsmappen", command=set_output_folder)
output_folder_button.pack(pady=5)

# Label for å vise valgt utgangsmappe
output_folder_label = StringVar()
output_folder_label.set("Ingen utgangsmappen valgt")
output_folder_info = Label(root, textvariable=output_folder_label)
output_folder_info.pack(pady=5)

# Knapp for å starte konverteringen
start_button = Button(root, text="Start konvertering", command=start_conversion)
start_button.pack(pady=20)

# Progressbar og label for å vise konverteringsprogresjon
progress_var = StringVar()
progress_bar = Progressbar(root, orient='horizontal', length=370, mode='determinate')
progress_bar.pack(pady=10)

progress_label = Label(root, textvariable=progress_var)
progress_label.pack(pady=5)

# Starter hovedløkken for GUI
root.mainloop()
