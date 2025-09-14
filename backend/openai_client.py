import openai
from settings import settings

# Set OpenAI API key from settings
openai.api_key = settings.OPENAI_API_KEY

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_response(self, messages: list) -> str:
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

openai_client = OpenAIClient()



