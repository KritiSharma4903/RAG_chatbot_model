from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)

def get_llm_response(question: str):

    prompt = ChatPromptTemplate.from_template("""
Answer the following question clearly:

Question: {question}
""")

    chain = prompt | llm

    response = chain.invoke({
        "question": question
    })

    return response.content

