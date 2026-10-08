from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from api.llm.llm import LLMService


class MultiQueryGenerator:

    PROMPT = ChatPromptTemplate.from_template(
        """
You are a legal search assistant.

Generate 4 different search queries that could retrieve
the correct legal information.

Return one query per line.

Question:
{question}
"""
    )

    @staticmethod
    def generate(question):

        llm = LLMService.get_llm()

        chain = (
            MultiQueryGenerator.PROMPT
            | llm
            | StrOutputParser()
        )

        result = chain.invoke(
            {
                "question": question
            }
        )

        queries = [
            q.strip()
            for q in result.split("\n")
            if q.strip()
        ]

        if question not in queries:
            queries.insert(0, question)

        return queries[:5]