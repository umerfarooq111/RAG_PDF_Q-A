from langchain_google_genai import ChatGoogleGenerativeAI

_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

class LLMService:
    @staticmethod
    def invoke(prompt: str):
        return _llm.invoke(prompt)
