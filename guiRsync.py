import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess


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


# Fonction pour exécuter rsync
def run_rsync():
    source = source_entry.get()
    destination = destination_entry.get()

    if not source or not destination:
        messagebox.showwarning("Erreur",
                               "Veuillez sélectionner les répertoires source et destination.")
        return

    # Construire la commande rsync
    rsync_command = ["rsync"]

    # Ajout des options sélectionnées par l'utilisateur
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

    try:
        # Exécuter la commande rsync
        result = subprocess.run(rsync_command, check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        messagebox.showinfo("Succès",
                            "Synchronisation terminée avec succès.\n\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur",
                             f"Erreur lors de l'exécution de rsync:\n\n{e.stderr}")


# Créer la fenêtre principale
root = tk.Tk()
root.title("Interface Graphique pour rsync")
root.geometry("600x400")

# Champ de saisie pour le répertoire source
tk.Label(root, text="Répertoire source:").pack(pady=5)
source_frame = tk.Frame(root)
source_frame.pack(pady=5)
source_entry = tk.Entry(source_frame, width=40)
source_entry.pack(side=tk.LEFT, padx=5)
tk.Button(source_frame, text="Parcourir",
          command=select_source).pack(side=tk.LEFT)

# Champ de saisie pour le répertoire destination
tk.Label(root, text="Répertoire destination:").pack(pady=5)
destination_frame = tk.Frame(root)
destination_frame.pack(pady=5)
destination_entry = tk.Entry(destination_frame, width=40)
destination_entry.pack(side=tk.LEFT, padx=5)
tk.Button(destination_frame, text="Parcourir",
          command=select_destination).pack(side=tk.LEFT)

# Options rsync avec description
tk.Label(root, text="Options rsync:",
         font=('Arial', 12, 'bold')).pack(pady=10)

# Variables pour chaque option
archive_var = tk.BooleanVar(
    value=True)  # Option -a par défaut activée
verbose_var = tk.BooleanVar(
    value=True)  # Option -v par défaut activée
human_readable_var = tk.BooleanVar(
    value=True)  # Option -h par défaut activée
compress_var = tk.BooleanVar()
progress_var = tk.BooleanVar()
delete_var = tk.BooleanVar()
dry_run_var = tk.BooleanVar()

# Cases à cocher pour les options
tk.Checkbutton(root,
               text="Mode archive (-a) : copie récursive et conserve les permissions",
               variable=archive_var).pack(anchor='w',
                                          padx=20)
tk.Checkbutton(root,
               text="Mode verbeux (-v) : affiche les informations détaillées pendant la copie",
               variable=verbose_var).pack(anchor='w',
                                          padx=20)
tk.Checkbutton(root,
               text="Format lisible (-h) : affiche la taille des fichiers de façon lisible",
               variable=human_readable_var).pack(anchor='w',
                                                 padx=20)
tk.Checkbutton(root,
               text="Compression (--compress) : compresse les données pendant le transfert",
               variable=compress_var).pack(anchor='w',
                                           padx=20)
tk.Checkbutton(root,
               text="Afficher la progression (--progress) : affiche la progression en temps réel",
               variable=progress_var).pack(anchor='w',
                                           padx=20)
tk.Checkbutton(root,
               text="Supprimer les fichiers obsolètes (--delete) : supprime les fichiers de destination absents de la source",
               variable=delete_var).pack(anchor='w',
                                         padx=20)
tk.Checkbutton(root,
               text="Simuler l'exécution (--dry-run) : affiche ce qui serait fait sans effectuer la copie",
               variable=dry_run_var).pack(anchor='w',
                                          padx=20)

# Bouton pour lancer rsync
tk.Button(root, text="Synchroniser", command=run_rsync,
          bg="green", fg="white").pack(pady=20)

# Boucle principale
root.mainloop()
