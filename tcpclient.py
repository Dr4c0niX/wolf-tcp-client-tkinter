import socket
import json
import tkinter as tk
from tkinter import messagebox

# Configuration de la connexion
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
    if response:
        messagebox.showinfo("Parties", f"ID des parties: {response['response']['id_parties']}")

def subscribe_to_party():
    player = entry_player.get()
    id_party = entry_id_party.get()
    response = send_request("subscribe", [{"player": player, "id_party": id_party}])
    if response:
        messagebox.showinfo("Inscription", f"Rôle: {response['response']['role']}, ID Joueur: {response['response']['id_player']}")

def create_gui():
    root = tk.Tk()
    root.title("Client TCP Tkinter")

    tk.Button(root, text="Lister les parties", command=list_parties).pack(pady=5)

    tk.Label(root, text="Nom du joueur:").pack()
    global entry_player
    entry_player = tk.Entry(root)
    entry_player.pack()

    tk.Label(root, text="ID de la partie:").pack()
    global entry_id_party
    entry_id_party = tk.Entry(root)
    entry_id_party.pack()

    tk.Button(root, text="S'inscrire à une partie", command=subscribe_to_party).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
 