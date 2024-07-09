# 🔍 **Lenze:** A search chatbot inspired by Perplexity AI.

## Features
Lenze is capable of doing:
- Search on web on user's query.
- Retrive summarised information regarding the query.
- Provide sources to each piece of information.
- Suggest related questions.
- Reference conversation history.

## Framework
Lenze utilises the [Netmind.AI-XYZ](https://github.com/protagolabs/Netmind-AI-XYZ) framework to manipulate multiple agents.

## Agents
Lenze consists of the following agents:

**Search Agent:** Search across the internet on the given query and return a list of sources containing URLs and text content at the URLs.
<br>There are two sub-agents that this agent calls:
- **Optimization Agent:** Optimize the query for most accurate Google search results.
- **Refining Agent:** Refined the search results to exclude irrelevant, redundant and unreliable sources.

**Response Agent:** Analyze the extracted information and generate a concise response to user's query.

**Interaction Agent:** Generate related questions and answer further questions, with reference to conversation history.

## Workflow
```mermaid
graph TB;
    A[User inputs query] --> B[Agent optimizes query];
    B --> C[Search online using the optimized query];
    C --> D[Agent refines search results];
    D --> E[Scrape text from sites in search results to produce sources];
    E --> F[Agent analyzes sources and generate response];
    F --> G[Agent suggests relevant queries]
```

## Getting Started
To get started, please create an ```.env``` file in the main directory of this repo.
<br>In the ```.env``` file, please insert the OpenAI API key, Google API key and your Google Custom Search Engine ID as below:
```
OPENAI_API_KEY = Your-OpenAI-API-Key
GOOGLE_API_KEY = Your-Google-API-Key
CSE_ID = Your-Google-CSE-ID
```
