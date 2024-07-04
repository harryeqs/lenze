from xyz.graph.auto_company import AutoCompany
from xyz.utils.llm.openai_client import OpenAIClient

from agents.search_agent import SearchAgent
from agents.summary_agent import SummaryAgent
from agents.interaction_agent import InteractionAgent


query = "What is the weather in Margate, UK today?"


if __name__ == "__main__":
    # args = set_args()

    llm_client = OpenAIClient(model="gpt-4-turbo")

    search_agent = SearchAgent(llm_client)
    summary_agent = SummaryAgent(llm_client)
    # interaction_agent = InteractionAgent(llm_client)

    staffs = [search_agent, summary_agent]

    company = AutoCompany(llm_client=llm_client)

    company.add_agent(staffs)

    company(user_input=query)
