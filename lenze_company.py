from xyz.graph.auto_company import AutoCompany
from xyz.utils.llm.openai_client import OpenAIClient

from agents.search_agent import SearchAgent
from agents.response_agent import ResponseAgent
from agents.interaction_agent import InteractionAgent
from agents.analysis_agent import AnalysisAgent

from tools.source_store import initialize_db
import time

if __name__ == "__main__":
    # Initialize sources storage
    initialize_db()
    
    llm_client = OpenAIClient(model="gpt-3.5-turbo", temperature=0)

    analysis_agent = AnalysisAgent(llm_client)
    search_agent = SearchAgent(llm_client)
    response_agent = ResponseAgent(llm_client)
    interaction_agent = InteractionAgent(llm_client)

    staffs = [analysis_agent, search_agent, response_agent, interaction_agent]

    company = AutoCompany(llm_client=llm_client)

    company.add_agent(staffs)

    query = input("\n========Welcome!========\nI am Lenze and I will help you with any query by searching online.\nPlease input your query: ")
    print("\n=======Calling the Company========")
    start_time = time.time()

    company(user_input=query)

    end_time = time.time()
    time_taken = f"Response took {end_time - start_time:.4f} seconds"
    print(time_taken)