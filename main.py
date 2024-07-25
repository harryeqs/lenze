from dotenv import load_dotenv
from openai import OpenAI
from lenze import Lenze
import os

if __name__ == '__main__':
    
    # Load environment variables
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    lenze = Lenze(client, model='gpt-4o-mini')
    
    lenze.run()