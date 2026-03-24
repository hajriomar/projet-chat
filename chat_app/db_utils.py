
import redis
from pymongo import MongoClient
import json
from datetime import datetime

# --- CONFIGURATION ---
MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

class ChatManager:
    def __init__(self):
        # Connexion MongoDB
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client['chat_database']
        self.messages_col = self.db['messages']
        
        # Connexion Redis
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def send_message(self, sender, text):
        message_data = {
            "sender": sender,
            "text": text,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # 1. Sauvegarde dans MongoDB (L'historique)
        self.messages_col.insert_one(message_data.copy())
        
        # 2. Publication dans Redis (Le direct / Temps réel)
        # On transforme le dictionnaire en texte (JSON) pour Redis
        self.redis_client.publish('chat_channel', json.dumps(message_data))
        
        print(f"Message de {sender} envoyé !")

# --- TEST RAPIDE ---
if __name__ == "__main__":
    chat = ChatManager()
    chat.send_message("Mariem", "Salut ! Mon chat fonctionne enfin !")
    # Ajoute ceci à la fin de ton test pour compter les messages
    count = chat.messages_col.count_documents({})
    print(f"Nombre total de messages dans MongoDB : {count}")