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

**Search agent:** Search across the internet on the given topic and return sources.

**Extraction agent:** Extract text content from the sources retrived.

**Summary agent:** Summarise the extracted information and generate a concise response.

**Interaction agent:** Generate related questions and answer further questions, with reference to conversation history.