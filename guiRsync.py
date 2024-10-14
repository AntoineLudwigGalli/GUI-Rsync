import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import threading


# Fonction pour sélectionner le répertoire source
def select_source():
    folder_selected = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder_selected)


# Fonction pour sélectionner le répertoire destination
def select_destination():
    folder_selected = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, folder_selected)


# Fonction pour exécuter rsync et mettre à jour l'affichage en temps réel
def run_rsync():
    source = source_entry.get()
    destination = destination_entry.get()

    if not source or not destination:
        messagebox.showwarning("Erreur",
                               "Veuillez sélectionner les répertoires source et destination.")
        return

    # Construire la commande rsync
    rsync_command = ["rsync", "-avh", "--progress"]

    # Ajouter les options sélectionnées
    if archive_var.get():
        rsync_command.append("-a")
    if verbose_var.get():
        rsync_command.append("-v")
    if human_readable_var.get():
        rsync_command.append("-h")
    if compress_var.get():
        rsync_command.append("--compress")
    if progress_var.get():
        rsync_command.append("--progress")
    if delete_var.get():
        rsync_command.append("--delete")
    if dry_run_var.get():
        rsync_command.append("--dry-run")

    rsync_command.append(source)
    rsync_command.append(destination)

    # Lancer le processus rsync dans un thread séparé pour ne pas bloquer l'interface
    threading.Thread(target=execute_rsync,
                     args=(rsync_command,)).start()


# Fonction d'exécution de la commande rsync avec mise à jour en temps réel
def execute_rsync(rsync_command):
    try:
        # Initialiser la barre de progression à 0
        progress_bar['value'] = 0
        output_text.delete(1.0,
                           tk.END)  # Vider la zone de texte

        # Exécuter rsync avec un pipe pour capturer la sortie en temps réel
        process = subprocess.Popen(rsync_command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)

        # Lire la sortie de rsync ligne par ligne
        total_files = 0
        for line in process.stdout:
            # Afficher la ligne dans la zone de texte
            output_text.insert(tk.END, line)
            output_text.see(
                tk.END)  # Faire défiler vers le bas

            # Compter les fichiers synchronisés et mettre à jour la barre de progression
            if "to-check=" in line:
                progress_info = line.split("to-check=")[
                    -1].strip()
                done, total = progress_info.split("/")
                done = int(done)
                total = int(total)
                total_files = total  # Nombre total de fichiers à synchroniser
                # Calculer le pourcentage de progression
                if total_files > 0:
                    progress = (
                                           total_files - done) / total_files * 100
                    progress_bar['value'] = progress

        process.wait()  # Attendre la fin du processus

        # Vérifier si rsync a réussi
        if process.returncode == 0:
            messagebox.showinfo("Succès",
                                "Synchronisation terminée avec succès.")
        else:
            messagebox.showerror("Erreur",
                                 "Erreur lors de l'exécution de rsync.")

    except Exception as e:
        messagebox.showerror("Erreur",
                             f"Une erreur s'est produite: {str(e)}")


# Créer la fenêtre principale
root = tk.Tk()
root.title("Interface Graphique pour rsync")
root.geometry("900x750")
root.configure(bg="#f0f4f7")  # Couleur de fond douce

# Style global
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat",
                background="#5DADE2", foreground="white",
                font=('Arial', 10, 'bold'))
style.configure("TCheckbutton", font=('Arial', 10),
                background="#f0f4f7")
style.configure("TLabel", font=('Arial', 10),
                background="#f0f4f7")
style.configure("TProgressbar", thickness=25,
                background="#5DADE2")

# Champ de saisie pour le répertoire source
tk.Label(root, text="Répertoire source:",
         font=('Arial', 12, 'bold'), bg="#f0f4f7").pack(
    pady=5)
source_frame = tk.Frame(root, bg="#f0f4f7")
source_frame.pack(pady=5)
source_entry = tk.Entry(source_frame, width=50,
                        font=('Arial', 10))
source_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(source_frame, text="Parcourir",
           command=select_source).pack(side=tk.LEFT)

# Champ de saisie pour le répertoire destination
tk.Label(root, text="Répertoire destination:",
         font=('Arial', 12, 'bold'), bg="#f0f4f7").pack(
    pady=5)
destination_frame = tk.Frame(root, bg="#f0f4f7")
destination_frame.pack(pady=5)
destination_entry = tk.Entry(destination_frame, width=50,
                             font=('Arial', 10))
destination_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(destination_frame, text="Parcourir",
           command=select_destination).pack(side=tk.LEFT)

# Options rsync avec description
tk.Label(root, text="Options rsync:",
         font=('Arial', 12, 'bold'), bg="#f0f4f7").pack(
    pady=10)

# Variables pour chaque option
archive_var = tk.BooleanVar(
    value=True)  # Option -a par défaut activée
verbose_var = tk.BooleanVar(
    value=True)  # Option -v par défaut activée
human_readable_var = tk.BooleanVar(
    value=True)  # Option -h par défaut activée
compress_var = tk.BooleanVar(value=True)
progress_var = tk.BooleanVar(
    value=True)  # Option --progress par défaut activée
delete_var = tk.BooleanVar()
dry_run_var = tk.BooleanVar()

# Cases à cocher pour les options avec marges ajustées
ttk.Checkbutton(root,
                text="Mode archive (-a) : copie récursive et conserve les permissions",
                variable=archive_var).pack(anchor='w',
                                           padx=20, pady=2)
ttk.Checkbutton(root,
                text="Mode verbeux (-v) : affiche les informations détaillées pendant la copie",
                variable=verbose_var).pack(anchor='w',
                                           padx=20, pady=2)
ttk.Checkbutton(root,
                text="Format lisible (-h) : affiche la taille des fichiers de façon lisible",
                variable=human_readable_var).pack(
    anchor='w', padx=20, pady=2)
ttk.Checkbutton(root,
                text="Compression (--compress) : compresse les données pendant le transfert",
                variable=compress_var).pack(anchor='w',
                                            padx=20, pady=2)
ttk.Checkbutton(root,
                text="Afficher la progression (--progress) : affiche la progression en temps réel",
                variable=progress_var).pack(anchor='w',
                                            padx=20, pady=2)
ttk.Checkbutton(root,
                text="Supprimer les fichiers obsolètes (--delete) : supprime les fichiers de destination absents de la source",
                variable=delete_var).pack(anchor='w',
                                          padx=20, pady=2)
ttk.Checkbutton(root,
                text="Simuler l'exécution (--dry-run) : affiche ce qui serait fait sans effectuer la copie",
                variable=dry_run_var).pack(anchor='w',
                                           padx=20, pady=2)

# Barre de progression stylisée
progress_bar = ttk.Progressbar(root, orient="horizontal",
                               length=500,
                               mode="determinate",
                               style="TProgressbar")
progress_bar.pack(pady=20)

# Zone de texte pour afficher la sortie en temps réel
output_text = tk.Text(root, height=20, width=120,
                      font=('Arial', 10), bg="#eaf2f8",
                      relief="flat")
output_text.pack(pady=10)

# Bouton pour lancer rsync
ttk.Button(root, text="Synchroniser",
           command=run_rsync).pack(pady=20)

# Boucle principale
root.mainloop()
