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

**Search agent:** Search across the internet on the given query and return a list of sources containing URLs and text content at the URLs.
<br>There are two sub-agents that this agent calls:
- **Optimization agent:** Optimize the query for most accurate Google search results.
- **Refining agent:** Refined the search results to exclude irrelevant, redundant and unreliable sources.

**Response agent:** Analyze the extracted information and generate a concise response to user's query.

**Interaction agent:** Generate related questions and answer further questions, with reference to conversation history.