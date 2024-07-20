from dotenv import load_dotenv
from openai import OpenAI
from lenze import Lenze
import os


# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
lenze = Lenze(client, model='gpt-3.5-turbo')

sub_queries = lenze.analyze('how much is apple vision pro in china')
print(sub_queries)