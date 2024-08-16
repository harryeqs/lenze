import sqlite3
import numpy as np
import openai
import os
from sklearn.metrics.pairwise import cosine_similarity
import time

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

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
                title TEXT,
                link TEXT,
                text TEXT,
                embedding BLOB
            )
        ''')
        conn.commit()
        conn.close()

    def generate_embedding(self, text):
        """
        Generate an embedding using the OpenAI API for the given text.
        """
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32).tobytes()

    def store_data(self, data):
        """
        Store data locally into the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_time = time.time()
        for entry in data:
            if entry['text'] and entry['text'] not in ['Error fetching content.', 'Enable JavaScript and cookies to continue', 'Please enable JS and disable any ad blocker', 'Access Denied']:
                embedding = self.generate_embedding(entry['text'])
                cursor.execute(f'''
                    INSERT INTO {self.table_name} (title, link, text, embedding) VALUES (?, ?, ?, ?)
                ''', (entry['title'], entry['link'], entry['text'], embedding))

        end_time = time.time()
        
        conn.commit()
        conn.close()

        print(f'Storing took {end_time-start_time:.4f} seconds')

    def read_data(self):
        """
        Read locally stored data from the SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT title, link, text, embedding FROM {self.table_name}')
        rows = cursor.fetchall()
        conn.close()

        data = [{'title': row[0], 'link': row[1], 'text': row[2], 'embedding': np.frombuffer(row[3], dtype=np.float32)} for row in rows]
        return data

    def find_most_relevant_sources(self, query_embedding, top_n=5, similarity_threshold=0.5, scope=20):
        """
        Find the most relevant sources based on cosine similarity.
        """
        sources = self.read_data()[-scope:]

        if not sources:
            print("No sources found in the database.")
            return []  # Return an empty list or handle this case as needed
        
        source_embeddings = [source['embedding'] for source in sources]
        similarities = cosine_similarity([query_embedding], source_embeddings).flatten()
        print(similarities)
        filtered_indices = [i for i, similarity in enumerate(similarities) if similarity > similarity_threshold]
        filtered_indices = sorted(filtered_indices, key=lambda i: similarities[i], reverse=True)
        most_relevant_indices = filtered_indices[:top_n]
        return [{'title': sources[i]['title'], 'link': sources[i]['link'], 'text': sources[i]['text']} for i in most_relevant_indices]
