from guardrails import Guard
from models import InvoiceSchema
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, RAG_LLM_MODEL

# Create Guard once
guard = Guard.for_pydantic(output_class=InvoiceSchema)

# Create LLM once
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=RAG_LLM_MODEL,
    temperature=0
)


def extract_invoice_data(text, question: str = None):

    messages = [
        {
            "role": "system",
            "content": "You are a strict invoice data extraction system. Do not guess values."
        },
        {
            "role": "user",
            "content": f"""
Extract invoice details STRICTLY from the given text.

Rules:
- Do NOT create or guess any values.
- Use EXACT text from the document.
- If missing, return null.
- Return ONLY valid JSON.

Invoice Text:
{text}
"""
        }
    ]

    def llm_callable(messages, **kwargs):
        response = llm.invoke(messages)
        return response.content

    validated_output = guard(
        llm_api=llm_callable,
        messages=messages
    )

    return validated_output.validated_output





