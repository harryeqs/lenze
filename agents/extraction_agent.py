__all__ = ["ExtractionAgent"]

from typing import Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient
from xyz.node.basic.llm_agent import LLMAgent
from tools.web_scraper import scrape_urls

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
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"}, 
                                "description": "The links to webpages where the information need to be extracted."}
                        },
                        "required": ["urls"]
                    },
                }
            }
        )
        self.input_type = "list"
        self.output_type = "dict"

        # self.llm_extraction = LLMAgent(template=extraction_prompt, llm_client=llm_client, stream=True)

    def flowing(self, urls: list):
        extracted_text = scrape_urls(urls)
        return extracted_text
    

extraction_prompt = [
    {
        "role": "system",
        "content": """
You are an assistant specialized in extracting the main content from web pages provided in a list of URLs. Follow these steps:

1. **Tool Usage**:
   - Use the `scrape_urls` tool to extract content from the provided URLs.
   - Notify the user: "Scraping content from URLs using 'scrape_urls'".

2. **Content Extraction**:
   - Extract the main text, excluding ads, navigation menus, headers, footers, and irrelevant sections.
   - Preserve the original text formatting for readability.

3. **Error Handling**:
   - If a URL is inaccessible, notify: "Error: Unable to access URL".
   - Ignore the inaccessible URL and DO NOT attempt to extract again.

4. **Output Format**:
   - Return the extracted texts as a JSON object, indexed by their URLs.

5. **Important Notice**:
   - Ensure the `scrape_urls` tool is used only once to avoid multiple extractions.

Provide the extracted content as described.
"""},
    {
        "role": "user",
        "content": """
Please extract the text from the URLs provided in the following list: {urls}.
Your response should be detailed, structured, and adhere to the constraints outlined above.
"""}]