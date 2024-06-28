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
                    "name": "SearchAgent",
                    "description": "This function can search across the internet on a topic provided by the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question here which need help.",
                            }
                        },
                        "required": ["question"],
                    },
                }
            }
        )
        self.input_type = "str"
        self.output_type = "list"

        self.llm_search = LLMAgent(template=extraction_prompt, llm_client=llm_client, stream=True)

    def flowing(self, question: str, tools = [scrape_pdf, scrape_webpage]) -> Any:
        return self.llm_search(question=question)
    


extraction_prompt = """
You are an extraction assistant that help user to extract information from a list of given urls. Extract only the informatino relevant to the question.
Use an appropriate to scrape the webpage based on the characteristic of the webpage.

The question:
{question}
List of urls of sources to extract information from:
{links}

PLease give me extracted texts from all the sources in the form of a dictionary, indexed by their url.
"""