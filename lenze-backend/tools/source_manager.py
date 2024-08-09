import sqlite3
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import os

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

class Sources:
    def __init__(self, session_id):
        self.session_id = session_id
        self.db_path = "./data/sources.db"  # Common database for all sessions
        self.table_name = f"sources_{session_id}"  # Unique table for each session
        self.initialize_sources()

    def initialize_sources(self):
        """
        Initialize the SQLite database.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT,
                text TEXT,
                embedding BLOB
            )
        ''')
        conn.commit()
        conn.close()

    def generate_embedding(self, text):
        """
        Generate a BERT embedding for the given text.
        """
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embedding.tobytes()

    def store_data(self, data):
        """
        Store data locally into the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for entry in data:
            if entry['text'] and entry['text'] not in ['Error fetching content.', 'Enable JavaScript and cookies to continue', 'Please enable JS and disable any ad blocker', 'Access Denied']:
                embedding = self.generate_embedding(entry['text'])
                cursor.execute(f'''
                    INSERT INTO {self.table_name} (link, text, embedding) VALUES (?, ?, ?)
                ''', (entry['link'], entry['text'], embedding))
        
        conn.commit()
        conn.close()

    def read_data(self):
        """
        Read locally stored data from the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT link, text, embedding FROM {self.table_name}')
        rows = cursor.fetchall()
        conn.close()

        data = [{'link': row[0], 'text': row[1], 'embedding': np.frombuffer(row[2], dtype=np.float32)} for row in rows]
        return data

    def find_most_relevant_sources(self, query_embedding, top_n=5, similarity_threshold=0.2):
        """
        Find the most relevant sources based on cosine similarity.
        """
        sources = self.read_data()

        if not sources:
            print("No sources found in the database.")
            return []  # Return an empty list or handle this case as needed
        
        source_embeddings = [source['embedding'] for source in sources]
        similarities = cosine_similarity([query_embedding], source_embeddings).flatten()
        filtered_indices = [i for i, similarity in enumerate(similarities) if similarity > similarity_threshold]
        filtered_indices = sorted(filtered_indices, key=lambda i: similarities[i], reverse=True)
        most_relevant_indices = filtered_indices[:top_n]
        return [{'link': sources[i]['link'], 'text': sources[i]['text']} for i in most_relevant_indices]