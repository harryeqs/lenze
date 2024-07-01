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
You are an extraction assistant that help user to extract information from a list of given urls.
Use an appropriate to scrape the webpage based on the characteristic of the webpage.

PLease give me extracted texts from all the sources in the form of a dictionary, indexed by their url.
Example output:
\{"url1" : "text1", "url2": "text2" \}
"""},
    {
        "role": "user",
        "content": """
The links to the urls:
{links}

Please give me the extracted text from the provided links.
"""}]