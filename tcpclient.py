#wolf-tcp-client-tkinter/tcpclient.py
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkFont
import socket
import json
import os
import sys
import subprocess

SERVER_HOST = 'localhost'
SERVER_PORT = 8888

# Couleurs pour le thème sombre
DARK_BG = "#2E2E2E"
DARK_FG = "#FFFFFF"
DARK_BUTTON = "#404040"
DARK_HIGHLIGHT = "#505050"
DARK_FRAME = "#363636"

# Variable globale pour stocker le choix de partie
selected_party_id = None
selected_role = None
root = None  # Variable globale pour stocker la référence à la fenêtre principale

def list_parties():
    global selected_party_id

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            request = json.dumps({"action": "list_parties"})
            s.sendall(request.encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            parties_info = json.loads(response)

            # Nettoyer le frame des parties
            for widget in parties_frame.winfo_children():
                widget.destroy()

            if not parties_info.get("id_parties"):
                lbl = tk.Label(parties_frame, text="Aucune partie disponible.",
                               font=default_font, bg=DARK_FRAME, fg=DARK_FG)
                lbl.pack(anchor='w', pady=5)
                return

            # Initialiser les variables pour le suivi des erreurs
            failed_parties = []

            # Créer le cadre principal avec défilement
            main_frame = tk.Frame(parties_frame, bg=DARK_FRAME, bd=2, relief=tk.RIDGE)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Optimiser les largeurs des colonnes - version plus compacte
            col_widths = [3, 12, 5, 5, 5, 5, 5, 5]  # Largeurs plus compactes
            headers = ["Sel", "Nom", "Grille", "Joueurs", "Vill.", "Loups", "Tours", "Durée"]

            # Configuration du tableau avec défilement horizontal et vertical
            canvas = tk.Canvas(main_frame, bg=DARK_FRAME, highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
            
            # Tableau en grid qui sera contenu dans le canvas
            table_frame = tk.Frame(canvas, bg=DARK_FRAME)

            # Configuration des colonnes avec poids
            for i in range(len(col_widths)):
                table_frame.columnconfigure(i, weight=col_widths[i])

            # Ajout des en-têtes
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                header_cell = tk.Label(table_frame, text=header, 
                                      bg=DARK_HIGHLIGHT, fg=DARK_FG,
                                      relief="groove", bd=2, font=default_font)
                header_cell.grid(row=0, column=i, sticky="nsew", padx=1)

            # Séparateur
            separator = tk.Frame(table_frame, height=2, bg=DARK_FG)
            separator.grid(row=1, column=0, columnspan=len(col_widths), sticky="ew")

            # Récupération des détails globaux
            party_details_response = get_all_parties_details()
            all_parties_details = party_details_response if party_details_response else {}

            # Traitement des parties
            selected_party_id = tk.IntVar(value=-1)
            row_index = 2
            
            for party_id in parties_info["id_parties"]:
                party_details = None
                if str(party_id) in all_parties_details:
                    party_details = all_parties_details[str(party_id)]
                else:
                    party_details = get_party_details(party_id)

                if not party_details:
                    failed_parties.append(party_id)
                    continue

                # Checkbox pour sélectionner une partie
                select_checkbox = tk.Checkbutton(table_frame, bg=DARK_FRAME, fg=DARK_FG,
                                             activebackground=DARK_FRAME, activeforeground=DARK_FG,
                                             selectcolor=DARK_HIGHLIGHT, command=lambda p_id=party_id: selected_party_id.set(p_id))
                select_checkbox.grid(row=row_index, column=0, sticky="nsew", padx=1)

                # Affichage des informations de partie avec ellipsis pour les textes longs
                title_text = party_details["title_party"]
                if len(title_text) > 12:  # Tronquer les titres trop longs
                    title_text = title_text[:9] + "..."
                
                # Créer des étiquettes avec un fond stable et s'adaptant à l'espace disponible
                tk.Label(table_frame, text=title_text, 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=1, sticky="nsew", padx=1)
                tk.Label(table_frame, text=f"{party_details['grid_rows']}x{party_details['grid_cols']}",
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=2, sticky="nsew", padx=1)
                tk.Label(table_frame, text=party_details["max_players"], 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=3, sticky="nsew", padx=1)
                tk.Label(table_frame, text=party_details["villagers_count"], 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=4, sticky="nsew", padx=1)
                tk.Label(table_frame, text=party_details["werewolves_count"], 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=5, sticky="nsew", padx=1)
                tk.Label(table_frame, text=party_details["max_turns"], 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=6, sticky="nsew", padx=1)
                tk.Label(table_frame, text=f"{party_details['turn_duration']}s", 
                       bg=DARK_FRAME, fg=DARK_FG, font=default_font).grid(row=row_index, column=7, sticky="nsew", padx=1)

                row_index += 1

            # Gestion des cas où aucune donnée n'est disponible
            if row_index == 2:
                main_frame.destroy()
                lbl = tk.Label(parties_frame, text="Erreur de chargement des données des parties.",
                               font=default_font, bg=DARK_FRAME, fg=DARK_FG)
                lbl.pack(anchor='w', pady=5)
            else:
                # Configuration du défilement
                canvas.create_window((0, 0), window=table_frame, anchor='nw')
                
                # Mise à jour obligatoire pour obtenir les dimensions correctes
                table_frame.update_idletasks()
                
                # Configuration du canvas et des barres de défilement
                canvas.configure(
                    scrollregion=canvas.bbox("all"),
                    yscrollcommand=v_scrollbar.set,
                    xscrollcommand=h_scrollbar.set
                )
                
                # Placement des barres de défilement
                canvas.pack(side="left", fill="both", expand=True)
                v_scrollbar.pack(side="right", fill="y")
                h_scrollbar.pack(side="bottom", fill="x")

                # Ajuster automatiquement la taille du canvas quand la fenêtre change
                def on_configure(event):
                    # Mettre à jour la région de défilement pour s'adapter à la taille
                    canvas.configure(scrollregion=canvas.bbox("all"))
                
                canvas.bind('<Configure>', on_configure)

            # Affichage des erreurs
            if failed_parties:
                messagebox.showwarning("Avertissement",
                    f"Impossible de récupérer les données pour les parties : {', '.join(map(str, failed_parties))}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur de connexion : {str(e)}")

def get_party_details(party_id):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            request = json.dumps({"action": "party_details", "party_id": party_id})
            s.sendall(request.encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        messagebox.showwarning("Avertissement", f"Erreur lors de la connexion au serveur: {e}")
        return None

def get_all_parties_details():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            request = json.dumps({"action": "all_parties_details"})
            s.sendall(request.encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        messagebox.showwarning("Avertissement", f"Erreur lors de la connexion au serveur: {e}")
        return None

def subscribe_to_party():
    if selected_party_id is None or selected_party_id.get() == -1:
        messagebox.showinfo("Erreur", "Veuillez sélectionner une partie d'abord.")
        return

    if selected_role is None or selected_role.get() == "":
        messagebox.showinfo("Erreur", "Veuillez choisir un rôle.")
        return

    id_party = selected_party_id.get()
    player = entry_player.get().strip()
    role = selected_role.get()

    if not player:
        messagebox.showinfo("Erreur", "Veuillez entrer un nom de joueur.")
        return

    data = {
        "player": player,
        "id_party": id_party,
        "role_preference": role
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            request = json.dumps({"action": "subscribe", **data})
            s.sendall(request.encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            result = json.loads(response)["response"]
            messagebox.showinfo("Inscription", f"Rôle attribué: {result['role']}, ID Joueur: {result['id_player']}")
            list_parties()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la connexion au serveur: {e}")

def start_solo_game():
    """
    Lance une partie en mode solo dans une interface Tkinter
    """
    global root  # Pour pouvoir masquer/réafficher la fenêtre principale
    
    player_name = entry_player.get().strip()
    role = selected_role.get()

    if not player_name:
        messagebox.showinfo("Erreur", "Veuillez entrer un nom de joueur.")
        return

    if not role:
        messagebox.showinfo("Erreur", "Veuillez choisir un rôle.")
        return
    
    # Sauvegarder temporairement la fenêtre principale
    root.withdraw()
    
    try:
        # Chemin vers le script du jeu en version Tkinter
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game-local-tk.py")
        
        # Convertir loup-garou en loup pour compatibilité
        actual_role = "villageois" if role == "villageois" else "loup"
        
        # Créer un processus pour exécuter le jeu avec interface Tkinter
        process = subprocess.Popen([sys.executable, script_path], 
                                  env=dict(os.environ, PLAYER_NAME=player_name, PLAYER_ROLE=role))
        
        # Attendre que le processus se termine
        process.wait()
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer le jeu solo: {e}")
    finally:
        # Réafficher la fenêtre principale
        root.deiconify()

def create_gui():
    global parties_frame, entry_player, default_font, selected_role, root  # Ajout de root ici

    root = tk.Tk()
    root.title("Client Loup-Garou")
    root.geometry("1000x650")  # Fenêtre plus grande pour une meilleure visibilité
    root.configure(bg=DARK_BG)
        # Rendre la fenêtre redimensionnable et gérer l'expansion des widgets
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    

    # Style pour les widgets ttk
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton", background=DARK_BUTTON, foreground=DARK_FG)
    style.configure("TScrollbar", background=DARK_BG, troughcolor=DARK_FRAME, arrowcolor=DARK_FG)

    # Définition d'une police par défaut
    default_font = tkFont.Font(family="Helvetica", size=11)

    # Frame titre
    title_frame = tk.Frame(root, bg=DARK_BG, pady=10)
    title_frame.pack(fill='x')
    tk.Label(title_frame, text="Jeu du Loup-Garou", font=tkFont.Font(family="Helvetica", size=18, weight="bold"),
             bg=DARK_BG, fg=DARK_FG).pack()

    # Bouton pour lister les parties
    button_frame = tk.Frame(root, bg=DARK_BG, pady=5)
    button_frame.pack(fill='x')
    refresh_btn = tk.Button(button_frame, text="Rafraîchir les parties", font=default_font,
                           command=list_parties, bg=DARK_BUTTON, fg=DARK_FG,
                           activebackground=DARK_HIGHLIGHT, activeforeground=DARK_FG)
    refresh_btn.pack(pady=5)

    # Frame pour afficher les parties (au milieu)
    parties_frame = tk.Frame(root, bg=DARK_FRAME, padx=10, pady=10)
    parties_frame.pack(fill='both', expand=True, padx=10, pady=5)

    # Frame du bas pour les contrôles de connexion
    bottom_frame = tk.Frame(root, bg=DARK_BG, padx=10, pady=10)
    bottom_frame.pack(fill='x', side=tk.BOTTOM)

    # Frame pour le pseudo et la sélection du rôle
    controls_frame = tk.Frame(bottom_frame, bg=DARK_BG)
    controls_frame.pack(fill='x', pady=5)

    # Division en deux colonnes
    left_column = tk.Frame(controls_frame, bg=DARK_BG)
    left_column.pack(side=tk.LEFT, fill='x', expand=True)

    right_column = tk.Frame(controls_frame, bg=DARK_BG)
    right_column.pack(side=tk.RIGHT, fill='x', expand=True, padx=(10, 0))

    # Champ de saisie pour le pseudo du joueur (colonne gauche)
    tk.Label(left_column, text="Nom du joueur:", font=default_font,
             bg=DARK_BG, fg=DARK_FG).pack(anchor='w', pady=(0, 5))

    entry_player = tk.Entry(left_column, font=default_font, bg=DARK_HIGHLIGHT, fg=DARK_FG,
                           insertbackground=DARK_FG)
    entry_player.pack(fill='x', pady=(0, 5))

    # Sélection du rôle (colonne droite)
    tk.Label(right_column, text="Préférence de rôle:", font=default_font,
             bg=DARK_BG, fg=DARK_FG).pack(anchor='w', pady=(0, 5))

    # Définir une valeur par défaut pour le rôle (villageois)
    selected_role = tk.StringVar(value="villageois")
    role_frame = tk.Frame(right_column, bg=DARK_BG)
    role_frame.pack(fill='x')

    villager_radio = tk.Radiobutton(role_frame, text="Villageois", variable=selected_role, value="villageois",
                                  font=default_font, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_HIGHLIGHT,
                                  activebackground=DARK_BG, activeforeground=DARK_FG)
    villager_radio.pack(side=tk.LEFT, padx=(0, 10))

    werewolf_radio = tk.Radiobutton(role_frame, text="Loup-Garou", variable=selected_role, value="loup-garou",
                                   font=default_font, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_HIGHLIGHT,
                                   activebackground=DARK_BG, activeforeground=DARK_FG)
    werewolf_radio.pack(side=tk.LEFT)

    # Boutons d'actions (inscription à une partie et mode solo)
    buttons_frame = tk.Frame(bottom_frame, bg=DARK_BG)
    buttons_frame.pack(fill='x', pady=10)

    # Division en deux colonnes pour les boutons
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    # Bouton d'inscription
    subscribe_btn = tk.Button(buttons_frame, text="S'inscrire à la partie", font=default_font,
                             command=subscribe_to_party, bg=DARK_BUTTON, fg=DARK_FG,
                             activebackground=DARK_HIGHLIGHT, activeforeground=DARK_FG)
    subscribe_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

    # Bouton mode solo
    solo_btn = tk.Button(buttons_frame, text="Mode Solo", font=default_font,
                        command=start_solo_game, bg=DARK_BUTTON, fg=DARK_FG,
                        activebackground=DARK_HIGHLIGHT, activeforeground=DARK_FG)
    solo_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    # Charger la liste des parties au démarrage
    list_parties()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
