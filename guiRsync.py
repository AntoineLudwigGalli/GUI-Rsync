import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, \
    ttk
import subprocess
import threading
import time

# Variable pour stocker le processus rsync afin de pouvoir l'annuler
process = None
cancel_rsync = False


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


# Fonction pour annuler proprement rsync
def cancel_operation():
    global cancel_rsync
    if process is not None:
        cancel_rsync = True
        process.terminate()
        messagebox.showinfo("Annulation",
                            "La synchronisation a été annulée.")


# Fonction pour exécuter rsync et mettre à jour l'affichage en temps réel
def run_rsync():
    global cancel_rsync
    cancel_rsync = False  # Réinitialiser l'état d'annulation

    source = source_entry.get()
    destination = destination_entry.get()

    if not source or not destination:
        messagebox.showwarning("Erreur",
                               "Veuillez sélectionner les répertoires source et destination.")
        return

    # Construire la commande rsync
    rsync_command = []

    # Si sudo est sélectionné, demander le mot de passe
    if sudo_var.get():
        password = simpledialog.askstring(
            "Mot de passe sudo",
            "Entrez votre mot de passe sudo :", show='*')
        if not password:
            messagebox.showerror("Erreur",
                                 "Le mot de passe sudo est requis pour continuer.")
            return
        rsync_command = ["sudo",
                         "-S"]  # Préparer sudo avec une entrée de mot de passe

    rsync_command.extend(["rsync", "-avh", "--progress"])

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
                     args=(rsync_command, password)).start()


# Fonction d'exécution de la commande rsync avec mise à jour en temps réel
def execute_rsync(rsync_command, password):
    global process, cancel_rsync
    start_time = time.time()
    total_files = 0

    try:
        # Initialiser la barre de progression à 0
        progress_bar['value'] = 0
        output_text.delete(1.0,
                           tk.END)  # Vider la zone de texte
        time_label.config(
            text="Durée restante : Calcul en cours...")

        # Exécuter rsync avec un pipe pour capturer la sortie en temps réel
        # Si sudo est utilisé, on doit fournir le mot de passe à sudo via stdin
        if "sudo" in rsync_command:
            process = subprocess.Popen(rsync_command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE,
                                       text=True)
            process.stdin.write(
                password + "\n")  # Envoyer le mot de passe sudo
            process.stdin.flush()
        else:
            process = subprocess.Popen(rsync_command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       text=True)

        # Variables pour suivre la progression
        files_done = 0
        last_checked = 0

        for line in process.stdout:
            if cancel_rsync:  # Vérifier si l'annulation a été demandée
                return

            # Afficher la ligne dans la zone de texte
            output_text.insert(tk.END, line)
            output_text.see(
                tk.END)  # Faire défiler vers le bas

            # Extraire les informations sur la progression
            if "to-check=" in line:
                progress_info = line.split("to-check=")[
                    -1].strip()
                done, total = progress_info.split("/")
                done = int(done)
                total = int(total)
                total_files = total  # Nombre total de fichiers à synchroniser
                files_done = total - done

                # Calculer le pourcentage de progression
                if total_files > 0:
                    progress = files_done / total_files * 100
                    progress_bar['value'] = progress

                    # Calculer le temps écoulé et estimer la durée restante
                    elapsed_time = time.time() - start_time
                    files_remaining = total_files - files_done

                    # Éviter une division par zéro si aucun fichier n'a encore été traité
                    if files_done > 0:
                        estimated_time_per_file = elapsed_time / files_done
                        remaining_time = estimated_time_per_file * files_remaining

                        # Mettre à jour l'affichage de la durée restante
                        mins, secs = divmod(
                            int(remaining_time), 60)
                        time_label.config(
                            text=f"Durée restante : {mins} min {secs} sec")

        process.wait()  # Attendre la fin du processus

        # Réinitialiser le processus si rsync a été annulé
        if cancel_rsync:
            return

        # Vérifier si rsync a réussi
        if process.returncode == 0:
            progress_bar['value'] = 100
            time_label.config(
                text="Synchronisation terminée.")
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
root.geometry("700x600")
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
compress_var = tk.BooleanVar()
progress_var = tk.BooleanVar(
    value=True)  # Option --progress par défaut activée
delete_var = tk.BooleanVar()
dry_run_var = tk.BooleanVar()
sudo_var = tk.BooleanVar()  # Ajout de l'option sudo

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
                text="Supprimer les fichiers dans la destination (--delete)",
                variable=delete_var).pack(anchor='w',
                                          padx=20, pady=2)
ttk.Checkbutton(root,
                text="Simuler l'exécution (--dry-run) : affiche ce qui serait fait sans effectuer la copie",
                variable=dry_run_var).pack(anchor='w',
                                           padx=20, pady=2)
ttk.Checkbutton(root, text="Exécuter en tant que sudo",
                variable=sudo_var).pack(anchor='w', padx=20,
                                        pady=2)

# Barre de progression stylisée
progress_bar = ttk.Progressbar(root, orient="horizontal",
                               length=500,
                               mode="determinate",
                               style="TProgressbar")
progress_bar.pack(pady=20)

# Label pour la durée restante
time_label = tk.Label(root, text="Durée restante : N/A",
                      font=('Arial', 10), bg="#f0f4f7")
time_label.pack(pady=5)

# Zone de texte pour afficher la sortie en temps réel
output_text = tk.Text(root, height=10, width=80,
                      font=('Arial', 10), bg="#eaf2f8",
                      relief="flat")
output_text.pack(pady=10)

# Bouton pour lancer rsync
ttk.Button(root, text="Synchroniser",
           command=run_rsync).pack(pady=10)

# Bouton pour annuler rsync
ttk.Button(root, text="Annuler",
           command=cancel_operation).pack(pady=10)

# Boucle principale
root.mainloop()
