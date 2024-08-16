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
        # Create an index on the embedding column for faster queries
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_embedding ON {self.table_name}(embedding);')
        conn.commit()
        conn.close()

    def generate_embeddings(self, texts):
        """
        Generate embeddings using the OpenAI API for the given texts in batch.
        """
        response = openai.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        embeddings = [np.array(e, dtype=np.float32).tobytes() for e in response.data[0].embedding]
        return embeddings

    def store_data(self, data):
        """
        Store data locally into the SQLite database using batch insertions.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_time = time.time()
        batch_data = []
        texts_for_embedding = []

        for entry in data:
            if entry['text'] and entry['text'] not in ['Error fetching content.', 'Enable JavaScript and cookies to continue', 'Please enable JS and disable any ad blocker', 'Access Denied']:
                texts_for_embedding.append(entry['text'])
                batch_data.append((entry['title'], entry['link'], entry['text']))

        embeddings = self.generate_embeddings(texts_for_embedding)

        batch_insert_data = [(batch_data[i][0], batch_data[i][1], batch_data[i][2], embeddings[i]) for i in range(len(batch_data))]

        cursor.executemany(f'''
            INSERT INTO {self.table_name} (title, link, text, embedding) VALUES (?, ?, ?, ?)
        ''', batch_insert_data)

        end_time = time.time()

        conn.commit()
        conn.close()

        print(f'Storing took {end_time-start_time:.4f} seconds')

    def read_data_streaming(self):
        """
        Read locally stored data from the SQLite database using streaming.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT title, link, text, embedding FROM {self.table_name}')
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield {'title': row[0], 'link': row[1], 'text': row[2], 'embedding': np.frombuffer(row[3], dtype=np.float32)}
        conn.close()

    def find_most_relevant_sources(self, query, top_n=5, similarity_threshold=0.5, scope=20):
        """
        Find the most relevant sources based on cosine similarity using vectorized operations.
        """
        sources = list(self.read_data_streaming())[-scope:]

        if not sources:
            print("No sources found in the database.")
            return []  # Return an empty list or handle this case as needed

        query_embedding = np.frombuffer(self.generate_embeddings([query])[0], dtype=np.float32)
        source_embeddings = np.stack([source['embedding'] for source in sources])
        similarities = cosine_similarity([query_embedding], source_embeddings).flatten()
        
        filtered_indices = np.where(similarities > similarity_threshold)[0]
        print(filtered_indices)
        if filtered_indices.size == 0:
            return []

        most_relevant_indices = filtered_indices[np.argsort(similarities[filtered_indices])][-top_n:]
        return [{'title': sources[i]['title'], 'link': sources[i]['link'], 'text': sources[i]['text']} for i in most_relevant_indices]
