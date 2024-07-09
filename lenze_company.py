from xyz.graph.auto_company import AutoCompany
from xyz.utils.llm.openai_client import OpenAIClient

from agents.search_agent import SearchAgent
from agents.response_agent import ResponseAgent
from agents.interaction_agent import InteractionAgent


query = "What is the weather like in London tomorrow?"

if __name__ == "__main__":
    # args = set_args()
    
    llm_client = OpenAIClient(model="gpt-4-turbo", temperature=0)

    search_agent = SearchAgent(llm_client)
    response_agent = ResponseAgent(llm_client)
    interaction_agent = InteractionAgent(llm_client)

    staffs = [search_agent, response_agent, interaction_agent]

    company = AutoCompany(llm_client=llm_client)

    company.add_agent(staffs)

    query = input("\n========Welcome!========\nI am Lenze and I will help you with any query by searching online.\nPlease input your query: ")
    print("\n=======Calling the Company========")
    company(user_input=query)
