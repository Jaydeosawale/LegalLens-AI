from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from api.llm.llm import LLMService


class QueryRewriter:

    PROMPT = ChatPromptTemplate.from_template(
        """
You are an expert legal search assistant.

Convert the user's question into the BEST search query
for retrieving legal documents.

Rules:

- Remove unnecessary words like:
  what
  which
  explain
  tell me
  define
  describe

- Keep legal terms.

- Expand the query with related keywords.

Examples:

Question:
What is Article 14?

Search Query:
Article 14 Equality before law Constitution of India

Question:
Explain Article 21

Search Query:
Article 21 Right to Life Constitution of India

Question:
Which article guarantees equality?

Search Query:
Article 14 Equality before law Constitution of India

Question:
Tell me about Fundamental Rights

Search Query:
Fundamental Rights Constitution of India

Return ONLY the search query.

Question:
{question}
"""
    )

    @staticmethod
    def rewrite(question: str) -> str:

        llm = LLMService.get_llm()

        chain = (
            QueryRewriter.PROMPT
            | llm
            | StrOutputParser()
        )

        query = chain.invoke(
            {
                "question": question
            }
        )

        print("=" * 80)
        print("ORIGINAL :", question)
        print("SEARCH   :", query)
        print("=" * 80)

        return query.strip()
