import os 
import rawpy 
import imageio 
from tkinter import Tk, filedialog, Button, Label, StringVar, OptionMenu 
from tkinter.ttk import Progressbar 
import threading  
import concurrent.futures

# Funksjon for å velge CR2-filer
def choose_files():
    file_paths = filedialog.askopenfilenames(title="Velg CR2-filer", filetypes=[("CR2 files", "*.cr2")])  # Åpner en dialog for å velge filer
    if file_paths:
        file_paths_label.set(f"Valgte filer: {len(file_paths)} filer valgt")  # Oppdaterer etiketten med antall valgte filer
    else:
        file_paths_label.set("Ingen filer valgt")  # Oppdaterer etiketten hvis ingen filer ble valgt
    return root.tk.splitlist(file_paths)  # Returnerer en liste med valgte filstier

# Funksjon for å velge utgangsmappen
def choose_output_folder():
    output_folder = filedialog.askdirectory(title="Velg utgangsmappen")  # Åpner en dialog for å velge utgangsmappen
    if output_folder:
        output_folder_label.set(f"{output_folder}")  # Oppdaterer etiketten med valgt utgangsmappen
    else:
        output_folder_label.set("Ingen utgangsmappen valgt")  # Oppdaterer etiketten hvis ingen utgangsmappen ble valgt
    return output_folder  # Returnerer stien til den valgte utgangsmappen

# Funksjon for å konvertere CR2-filer til ønsket format (jpeg eller png)
def convert_cr2_to_format(file_path, output_folder, format='jpeg'):
    try:
        # Sjekk om formatet er gyldig
        if format not in ['jpeg', 'png']:
            raise ValueError("Format must be 'jpeg' eller 'png'")  # Kaster en feilmelding hvis formatet er ugyldig

        # Opprett utgangsmappen hvis den ikke eksisterer
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Oppretter utgangsmappen

        file_name = os.path.basename(file_path)  # Henter filnavnet fra stien
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.{format}")  # Lager hele utgangsstien

        # Les CR2-filen og konverter den til ønsket format
        with rawpy.imread(file_path) as raw:
            rgb = raw.postprocess()  # Behandler råfilen til et RGB-bilde
            imageio.imwrite(output_path, rgb)  # Skriver det behandlede bildet til utgangsstien
            print(f"Converted {file_name} to {format.upper()}")  # Skriver ut en melding om konverteringens status
        return file_path  # Returnerer filstien for å indikere suksess
    except Exception as e:
        print(f"Failed to convert {file_path}: {e}")  # Skriver ut en feilmelding hvis konverteringen feilet
        return None  # Returnerer None for å indikere feil

# Start konverteringen
def start_conversion():
    if not file_paths or not output_folder:
        progress_var.set("Velg filer og utgangsmappen først!")  # Oppdaterer etiketten hvis filer eller utgangsmappen ikke er valgt
        return

    format = format_var.get()  # Henter det valgte formatet fra GUI
    progress_bar['maximum'] = len(file_paths)  # Setter fremdriftsindikatorens maksimumsverdi

    # Kjør konverteringen i en egen tråd
    def run_conversion():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(convert_cr2_to_format, file_path, output_folder, format) for file_path in file_paths]  # Sender oppgaver til trådpuljen
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if future.result():
                    progress_bar['value'] = i + 1  # Oppdaterer fremdriftsindikatoren
                    progress_var.set(f"Ferdig: {i + 1}/{len(file_paths)}")  # Oppdaterer etiketten med fremdrift
                    root.update_idletasks()  # Oppdaterer GUI
            
        progress_var.set("Konvertering fullført!")  # Oppdaterer etiketten når konverteringen er fullført

    threading.Thread(target=run_conversion).start()  # Starter konverteringen i en egen tråd

# Sett filstiene
def set_file_paths():
    global file_paths
    file_paths = choose_files()  # Kaller funksjonen for å velge filer

# Sett utgangsmappen
def set_output_folder():
    global output_folder
    output_folder = choose_output_folder()  # Kaller funksjonen for å velge utgangsmappen

root = Tk()  # Initialiserer hovedvinduet for GUI
root.title("CR2 til PNG/JPEG Konverterer | Laget av Henrik S")  # Setter tittelen på vinduet
root.geometry("550x400")  # Setter størrelsen på vinduet

# Legg til stil
style = Style()
style.configure("TButton", font=("Helvetica", 10))  # Stil for knapper
style.configure("TLabel", font=("Helvetica", 10))  # Stil for etiketter
style.configure("TOptionMenu", font=("Helvetica", 10))  # Stil for valgmenyen
style.configure("TProgressbar", thickness=20)  # Stil for fremdriftsindikatoren

# Brukergrensesnitt for å velge konverteringsformat
label = Label(root, text="Velg konverteringsformat:")  # Legger til en etikett for å velge format
label.pack(pady=10)

format_var = StringVar(root)  # Oppretter en StringVar for formatvalg
format_var.set('png')  # Setter standardverdien til 'png'

format_menu = OptionMenu(root, format_var, 'png', 'jpeg')  # Lager en valgmeny for formater
format_menu.pack(pady=5)

# Knapp for å velge filer
file_button = Button(root, text="Velg filer", command=set_file_paths)  # Lager en knapp for å velge filer
file_button.pack(pady=5)

file_paths_label = StringVar()  # Lager en StringVar for å vise valgte filer
file_paths_label.set("Ingen filer valgt")  # Setter standardtekst for filvalg
file_paths_info = Label(root, textvariable=file_paths_label)  # Lager en etikett for å vise filvalg
file_paths_info.pack(pady=5)

# Knapp for å velge utgangsmappen
output_folder_button = Button(root, text="Velg utgangsmappen", command=set_output_folder)  # Lager en knapp for å velge utgangsmappen
output_folder_button.pack(pady=5)

output_folder_label = StringVar()  # Lager en StringVar for å vise valgt utgangsmappen
output_folder_label.set("Ingen utgangsmappen valgt")  # Setter standardtekst for utgangsmappen
output_folder_info = Label(root, textvariable=output_folder_label)  # Lager en etikett for å vise utgangsmappen
output_folder_info.pack(pady=5)

# Knapp for å starte konvertering
start_button = Button(root, text="Start konvertering", command=start_conversion)  # Lager en knapp for å starte konverteringen
start_button.pack(pady=20)

# Fremdriftsindikator
progress_var = StringVar()  # Lager en StringVar for fremdriftsindikatoren
progress_bar = Progressbar(root, orient='horizontal', length=370, mode='determinate')  # Lager en fremdriftsindikator
progress_bar.pack(pady=10)

progress_label = Label(root, textvariable=progress_var)  # Lager en etikett for fremdriftsindikatoren
progress_label.pack(pady=5)

root.mainloop()  # Starter hovedløkken for GUI
