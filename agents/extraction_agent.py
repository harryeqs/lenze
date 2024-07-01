__all__ = ["ExtractionAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.web_scraper import scrape_webpage, scrape_pdf

class ExtractionAgent(Agent):

    def __init__(self, llm_client: OpenAIClient):
        super().__init__()

        self.set_information(
            {
                "type": "function",
                "function": {
                    "name": "ExtractionAgent",
                    "description": "This function can extract text content from the provided urls.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "links": {"type": "list", "description": "The links to webpages where the information need to be extracted."}
                        },
                        "required": ["links"],
                    },
                }
            }
        )
        self.input_type = "list"
        self.output_type = "dict"

        self.llm_search = LLMAgent(template=extraction_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, links: list) -> Any:
        return self.llm_search(links=links, tools=[scrape_pdf, scrape_webpage])
    

extraction_prompt = [
    {
        "role": "system",
        "content": """
You are an extraction assistant designed to help users extract information from a list of given URLs. Follow these guidelines:

1. Use the appropriate method to scrape each webpage based on its characteristics (e.g., HTML structure, content type).
2. Ensure that only the main content is extracted, excluding advertisements, navigation menus, and other irrelevant sections.
3. Preserve the original formatting of the text as much as possible to maintain readability.
4. If a URL is inaccessible or results in an error, notify the user and skip that URL.

Provide the extracted texts from all the sources in the form of a dictionary, indexed by their URLs.

Example output:
{
    "http://example.com/url1": "Extracted text from URL 1",
    "http://example.com/url2": "Extracted text from URL 2"
}
"""},
    {
        "role": "user",
        "content": """
The links to the urls:
{links}

Please provide the extracted text from the provided links, adhering to the above constraints.
"""}]