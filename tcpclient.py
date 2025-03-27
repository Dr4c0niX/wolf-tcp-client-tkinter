import socket
import json
import tkinter as tk
from tkinter import messagebox

# Configuration de la connexion (port mis à jour pour correspondre au serveur)
HOST, PORT = "localhost", 9999

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
            response = sock.recv(1024).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la connexion au serveur: {e}")
        return None

def list_parties():
    response = send_request("list", [])
    if response and response["status"] == "OK":
        parties = response["response"]["id_parties"]
        for widget in parties_frame.winfo_children():
            widget.destroy()
        for id_party in parties:
            tk.Label(parties_frame, text=f"Partie {id_party}:").pack(anchor='w')
            tk.Button(parties_frame, text="S'inscrire", command=lambda id=id_party: subscribe_to_party(id)).pack(anchor='w')
    else:
        messagebox.showinfo("Parties", "Aucune partie disponible.")

def subscribe_to_party(id_party):
    player = entry_player.get() if entry_player.get() else f"Player_{id_party}"
    parameters = [
        {
            "player": player, 
            "id_party": id_party  # Utiliser les clés attendues par le serveur
        }
    ]
    response = send_request("subscribe", parameters)
    if response and response["status"] == "OK":
        messagebox.showinfo("Inscription", f"Rôle: {response['response']['role']}, ID Joueur: {response['response']['id_player']}")
    else:
        messagebox.showerror("Erreur", "L'inscription a échoué.")

def create_gui():
    global parties_frame
    global entry_player

    root = tk.Tk()
    root.title("Client TCP Tkinter")

    # Frame pour afficher les parties
    parties_frame = tk.Frame(root)
    parties_frame.pack(pady=5)

    # Bouton pour lister les parties
    tk.Button(root, text="Lister les parties", command=list_parties).pack(pady=5)

    # Champ de saisie pour le pseudo du joueur
    tk.Label(root, text="Nom du joueur (optionnel):").pack()
    entry_player = tk.Entry(root)
    entry_player.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()