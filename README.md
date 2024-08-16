# Lenze: An AI-Powered Search Engine

## Overview
**Lenze** is an advanced, open-source search engine designed to provide intelligent and concise responses to user queries by leveraging the power of artificial intelligence. Inspired by industry-leading platforms like Perplexity AI and its open-source counterpart Perplexica, Lenze goes beyond traditional search engines by not just retrieving relevant information from the web but also synthesizing it into clear, concise, and informative answers.

Lenze’s AI-driven capabilities allow it to parse complex queries, understand context, and deliver precise answers while referencing credible sources. This ensures users receive accurate and reliable information quickly, without needing to sift through multiple search results.

### Key features
- **AI-Powered Search:** Lenze uses AI algorithms to understand and respond to natural language queries, providing users with direct answers rather than a list of links.
- **Source Referencing:** For every answer provided, Lenze includes references to the sources of information, allowing users to verify and explore further.
- **Contextual Understanding:** Unlike traditional search engines, Lenze can interpret the context of a query, delivering more relevant and specific results.

## Technolgy Stack

**Backend Framework:** FastAPI

**Frontend Framework:** React

**Large Language Model:** OpenAI *GPT-4o-mini*

**Embedding Model:** OpenAI *text-embedding-3-small*

## Getting started

1. Clone this Github repo:
```
git clone https://github.com/harryeqs/lenze.git
```
2. Enter the directory of this repo.
3. Enter the frontend folder and install ```npm```:
```
cd lenze-frontend
npm install
```
4. Go back to the main directory and create a ```.env``` file.
<br>In the ```.env``` file, please insert the OpenAI API key, Google API key and your Google Custom Search Engine ID as below:
```
OPENAI_API_KEY = Your-OpenAI-API-Key
GOOGLE_API_KEY = Your-Google-API-Key
CSE_ID = Your-Google-CSE-ID
```
5. Make the ```start.sh``` file executable:
```chmod +x filename.sh```
6. Run the ```start.sh```:
```./start.sh```