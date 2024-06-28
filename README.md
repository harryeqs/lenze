# *Lenze:* A search chatbot inspired by Perplexity AI.

## Features
Lenze is designed to complete the following task:
- Search across the internet on a topic given by the user.
- Return information regarding the internet.
- Provide sources to each piece of information

## Framework
Lenze utilises the [Netmind.AI-XYZ](https://github.com/protagolabs/Netmind-AI-XYZ) framework to manipulate multiple agents.

## Agents
Lenze consists of the following agents:

**Search agent:** Search across the internet on the given topic and return sources.

**Extraction agent:** Extract text content from the sources found.

**Summary agent:** Summarise the text content extracted from each source.

**Reference agent:** Keep track of the source of each piece of information summarised and produce a final output.