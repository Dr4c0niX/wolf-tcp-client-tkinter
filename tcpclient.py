import socket
import json
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkFont

# Configuration de la connexion
HOST, PORT = "localhost", 8888

# Couleurs du thème sombre
DARK_BG = "#2E2E2E"
DARK_FRAME = "#3E3E3E"
DARK_HIGHLIGHT = "#505050"
DARK_BUTTON = "#4A4A4A"
DARK_FG = "#FFFFFF"

def send_request(action, parameters):
    """Envoie une requête au serveur et retourne la réponse."""
    request = {
        "action": action,
        "parameters": parameters
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            sock.sendall(json.dumps(request).encode('utf-8'))
            response_data = sock.recv(4096)
            if response_data:
                return json.loads(response_data.decode('utf-8'))
            return None
    except Exception as e:
        messagebox.showerror("Erreur de connexion", f"Impossible de communiquer avec le serveur: {e}")
        return None
def list_parties():
    global selected_party_id
    response = send_request("list_parties", {})
    if response and response.get("status") == "OK":
        parties_info = response.get("response", {})

        # Nettoyer le frame des parties
        for widget in parties_frame.winfo_children():
            widget.destroy()

        if not parties_info.get("id_parties"):
            lbl = tk.Label(parties_frame, text="Aucune partie disponible.",
                           font=default_font, bg=DARK_FRAME, fg=DARK_FG)
            lbl.pack(anchor='w', pady=5)
        else:
            # Initialiser la variable de sélection
            selected_party_id = tk.IntVar(value=-1)
        if not parties_info.get("id_parties"):
            lbl = tk.Label(parties_frame, text="Aucune partie disponible.",
                           font=default_font, bg=DARK_FRAME, fg=DARK_FG)
            lbl.pack(anchor='w', pady=5)
        else:
            # Initialiser la variable de sélection
            selected_party_id = tk.IntVar(value=-1)

            # Tailles fixes des colonnes en caractères
            col_widths = [10, 25, 10, 12, 12, 12]
            headers = ["Sélection", "Nom de partie", "Grille", "Max joueurs", "Villageois", "Loups-garous"]

            # Cadre principal avec marge pour les défilements
            main_frame = tk.Frame(parties_frame, bg=DARK_FRAME, bd=2, relief=tk.RIDGE)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Créer canvas et scrollbar pour le défilement
            canvas = tk.Canvas(main_frame, bg=DARK_FRAME)
            scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            # Configurer les colonnes dans le tableau
            for i, width in enumerate(col_widths):
                table_frame.columnconfigure(i, weight=1 if i == 1 else 0, minsize=width*7)

            # Cadre intérieur qui contient tout le tableau
            table_frame = tk.Frame(canvas, bg=DARK_FRAME)

            # Configurer les colonnes dans le tableau
            total_width = sum(col_widths)
            for i, width in enumerate(col_widths):
                table_frame.columnconfigure(i, weight=1 if i == 1 else 0, minsize=width*7)

            # En-têtes des colonnes
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                header_cell = tk.Label(table_frame, text=header, width=width,
                                      bg=DARK_HIGHLIGHT, fg=DARK_FG,
                                      relief="groove", bd=2, font=default_font)
                header_cell.grid(row=0, column=i, sticky="nsew")

            # Ligne de séparation entre l'en-tête et les données
            separator = tk.Frame(table_frame, height=2, bg=DARK_FG)
            separator.grid(row=1, column=0, columnspan=len(col_widths), sticky="ew")

            # Variables pour tracer les lignes verticales
            vertical_lines = []

            # Ajouter les données des parties
            row_index = 2  # Commencer après l'en-tête et le séparateur

            for party_id in parties_info.get("id_parties", []):
                party_details = parties_info["parties_details"].get(str(party_id), {})

                # Aligner les séparateurs verticaux
                if row_index == 2:
                    # Créer les séparateurs verticaux (une seule fois)
                    for i in range(len(col_widths) - 1):
                        vertical_line = tk.Frame(table_frame, width=2, bg=DARK_FG)
                        # Le placer à la jonction entre les colonnes
                        vertical_line.grid(row=0, column=i, rowspan=1000,
                                          sticky="nse", padx=0)
                        vertical_lines.append(vertical_line)

                # Radio button pour la sélection
                radio_btn = tk.Radiobutton(table_frame, variable=selected_party_id, value=party_id,
                                          bg=DARK_FRAME, fg=DARK_FG, selectcolor=DARK_HIGHLIGHT,
                                          activebackground=DARK_BG, activeforeground=DARK_FG)
                radio_btn.grid(row=row_index, column=0, padx=10, pady=5, sticky="ns")

                # Nom de la partie
                title = party_details.get("title", f"Partie {party_id}")
                # Tronquer le titre s'il est trop long pour éviter les débordements
                if len(title) > col_widths[1] - 2:  # -2 pour la marge
                    title = title[:col_widths[1] - 5] + "..."

                title_lbl = tk.Label(table_frame, text=title, bg=DARK_FRAME, fg=DARK_FG,
                                    anchor="center", font=default_font)
                title_lbl.grid(row=row_index, column=1, padx=5, pady=5, sticky="nsew")

                # Taille de la grille
                grid_size = party_details.get('grid_size', 10)
                grid_lbl = tk.Label(table_frame, text=f"{grid_size}×{grid_size}",
                                   bg=DARK_FRAME, fg=DARK_FG, anchor="center", font=default_font)
                grid_lbl.grid(row=row_index, column=2, padx=5, pady=5, sticky="nsew")

                # Max joueurs
                max_players = f"{party_details.get('current_players', 0)}/{party_details.get('max_players', 8)}"
                max_players_lbl = tk.Label(table_frame, text=max_players, bg=DARK_FRAME, fg=DARK_FG,
                                          anchor="center", font=default_font)
                max_players_lbl.grid(row=row_index, column=3, padx=5, pady=5, sticky="nsew")

                # Villageois
                villagers = party_details.get('villagers_count', 0)
                villagers_lbl = tk.Label(table_frame, text=str(villagers), bg=DARK_FRAME, fg=DARK_FG,
                                       anchor="center", font=default_font)
                villagers_lbl.grid(row=row_index, column=4, padx=5, pady=5, sticky="nsew")

                # Loups-garous
                werewolves = party_details.get('werewolves_count', 0)
                werewolves_lbl = tk.Label(table_frame, text=str(werewolves), bg=DARK_FRAME, fg=DARK_FG,
                                        anchor="center", font=default_font)
                werewolves_lbl.grid(row=row_index, column=5, padx=5, pady=5, sticky="nsew")

                # Ligne horizontale entre chaque rangée
                row_index += 1
                separator = tk.Frame(table_frame, height=2, bg=DARK_FG)
                separator.grid(row=row_index, column=0, columnspan=len(col_widths), sticky="ew", pady=2)
                row_index += 1

            # Configuration du canvas et de la scrollbar
            canvas.create_window((0, 0), window=table_frame, anchor="nw")
            table_frame.update_idletasks()  # Mettre à jour les mesures

            # Configurer la taille du canvas et le comportement de défilement
            canvas.configure(yscrollcommand=scrollbar.set,
                            scrollregion=canvas.bbox("all"),
                            width=table_frame.winfo_width(),
                            height=min(350, table_frame.winfo_height()))

            # Placement des éléments
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
def subscribe_to_party():
    global selected_party_id
    if selected_party_id is None or selected_party_id.get() == -1:
        messagebox.showinfo("Erreur", "Veuillez sélectionner une partie d'abord.")
        return
    else:
        messagebox.showinfo("Erreur", "Impossible de récupérer les parties.")

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

    parameters = {
        "player": player,
        "id_party": id_party,
        "role_preference": role  # Ajout de la préférence de rôle
    }

    response = send_request("subscribe", parameters)
    if response and response.get("status") == "OK":
        result = response["response"]
        messagebox.showinfo("Inscription", f"Rôle attribué: {result['role']}, ID Joueur: {result['id_player']}")
        list_parties()  # Rafraîchir la liste des parties
    else:
        messagebox.showinfo("Erreur", "Impossible de s'inscrire à la partie.")

def start_solo_game():
    """
    Lance une partie en mode solo (contre des IA)
    """
    player_name = entry_player.get().strip()
    role = selected_role.get()

    if not player_name:
        messagebox.showinfo("Erreur", "Veuillez entrer un nom de joueur.")
        return

    if not role:
        messagebox.showinfo("Erreur", "Veuillez choisir un rôle.")
        return

    parameters = {
        "player_name": player_name,
        "role_preference": role,
        "solo_mode": True
    }

    response = send_request("create_solo_game", parameters)
    if response and response.get("status") == "OK":
        result = response["response"]
        messagebox.showinfo("Partie Solo", f"Partie solo créée ! ID Partie: {result.get('id_party')}, ID Joueur: {result.get('id_player')}")
        list_parties()  # Rafraîchir la liste des parties
    else:
        messagebox.showinfo("Erreur", "Impossible de créer une partie solo.")

def create_gui():
    global parties_frame, entry_player, default_font, selected_role, selected_party_id
    # Initialize global variable
    selected_party_id = None

def create_gui():
    global parties_frame, entry_player, default_font, selected_role

    root = tk.Tk()
    root.title("Client Loup-Garou")
    root.geometry("900x600")  # Fenêtre plus grande pour accommoder les colonnes supplémentaires
    root.configure(bg=DARK_BG)

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
