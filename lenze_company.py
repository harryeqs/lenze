import argparse

from xyz.graph.auto_company import AutoCompany
from xyz.utils.llm.openai_client import OpenAIClient

from agents.search_agent import SearchAgent
from agents.extraction_agent import ExtractionAgent
from agents.summary_agent import SummaryAgent
# from agents.interaction_agent import InteractionAgent


def set_args():
    parser = argparse.ArgumentParser(description="Lenze Company")
    parser.add_argument("--question", type=str, default="Where does banana grow?",
                        help="The question which need help.")

    return parser.parse_args()


if __name__ == "__main__":
    args = set_args()

    llm_client = OpenAIClient(model="gpt-4-turbo")

    search_agent = SearchAgent(llm_client)
    extraction_agent = ExtractionAgent(llm_client)
    summary_agent = SummaryAgent(llm_client)
    # interaction_agent = InteractionAgent(llm_client)

    staffs = [search_agent, extraction_agent, summary_agent]

    company = AutoCompany(llm_client=llm_client)

    company.add_agent(staffs)

    company(user_input=args.question)