import sqlite3
import os
import numpy as np
from dotenv import load_dotenv
import openai
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import time

DB_PATH = 'data/sources.db'
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def initialize_db():
    """
    Initialize the SQLite database.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT,
            text TEXT,
            embedding BLOB
        )
    ''')
    cursor.execute('DELETE FROM sources')
    conn.commit()
    conn.close()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def generate_embedding(text):
    """
    Generate a BERT embedding for the given text.
    """
    start_time = time.time()
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    end_time = time.time()
    #print(f"Embedding generation took {end_time - start_time:.4f} seconds")
    return embedding.tobytes()

def local_store(data):
    """
    Store data locally into the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for entry in data:
        if entry['text'] and entry['text'] not in ['Error fetching content.', 'Enable JavaScript and cookies to continue', 'Please enable JS and disable any ad blocker', 'Access Denied']:
            embedding = generate_embedding(entry['text'])
            cursor.execute('''
                INSERT INTO sources (link, text, embedding) VALUES (?, ?, ?)
            ''', (entry['link'], entry['text'], embedding))
    
    conn.commit()
    conn.close()
    # print("Sources stored successfully.")

def find_most_relevant_sources(query_embedding, sources, top_n=5):
    """
    Find the most relevant sources based on cosine similarity.
    """
    source_embeddings = [source['embedding'] for source in sources]
    similarities = cosine_similarity([query_embedding], source_embeddings).flatten()
    most_relevant_indices = similarities.argsort()[-top_n:][::-1]
    return [{'link': sources[i]['link'], 'text': sources[i]['text']} for i in most_relevant_indices]

def local_read():
    """
    Read locally stored data from the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT link, text, embedding FROM sources')
    rows = cursor.fetchall()
    conn.close()

    data = [{'link': row[0], 'text': row[1], 'embedding': np.frombuffer(row[2], dtype=np.float32)} for row in rows]
    return data