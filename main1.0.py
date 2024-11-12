import os
import rawpy
import imageio
from tkinter import Tk, filedialog, Button, Label, StringVar
from tkinter.ttk import Progressbar
import threading

def choose_files():
    root = Tk()
    root.withdraw()  # Skjul hovedvinduet
    file_paths = filedialog.askopenfilenames(title="Velg CR2-filer", filetypes=[("CR2 files", "*.cr2")])
    return root.tk.splitlist(file_paths)

def convert_cr2_to_format(file_paths, output_folder, format='jpeg'):
    if format not in ['jpeg', 'png']:
        raise ValueError("Format must be 'jpeg' eller 'png'")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    progress_bar['maximum'] = len(file_paths)
    for i, file_path in enumerate(file_paths):
        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.{format}")

        with rawpy.imread(file_path) as raw:
            rgb = raw.postprocess()
            imageio.imwrite(output_path, rgb)
            print(f"Converted {file_name} to {format.upper()}")

        progress_bar['value'] = i + 1
        progress_var.set(f"Ferdig: {i + 1}/{len(file_paths)}")
        root.update_idletasks()

    progress_var.set("Konvertering fullført!")

def start_conversion(format):
    file_paths = choose_files()
    output_folder = filedialog.askdirectory(title="Velg utgangsmappen")
    if output_folder:
        threading.Thread(target=convert_cr2_to_format, args=(file_paths, output_folder, format)).start()

root = Tk()
root.title("CR2 til PNG/JPEG Konverterer | Laget av Henrik S")
root.geometry("460x230")  # Sett størrelsen på vinduet til 460x230 piksler

label = Label(root, text="Velg konverteringsformat:")
label.pack(pady=25)

jpeg_button = Button(root, text="Konverter til JPEG", command=lambda: start_conversion('jpeg'))
jpeg_button.pack(pady=5)

png_button = Button(root, text="Konverter til PNG", command=lambda: start_conversion('png'))
png_button.pack(pady=5)

progress_var = StringVar()
progress_bar = Progressbar(root, orient='horizontal', length=370, mode='determinate')
progress_bar.pack(pady=15)

progress_label = Label(root, textvariable=progress_var)
progress_label.pack(pady=5)

root.mainloop()