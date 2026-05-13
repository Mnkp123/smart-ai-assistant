from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

def get_ai_response(user_message, conversation_history, context=""):
    system_prompt = """You are a professional AI business assistant for SMEs.

CRITICAL RULES:
1. ALWAYS reply in ENGLISH only, no matter what language user writes in
2. Be professional, helpful and concise
3. Do NOT make up prices or features - only use information from context
4. If no context is provided, give general business advice
5. Never use Hindi or any other language - ENGLISH ONLY
"""
    if context:
        system_prompt += f"\n\nUse this document information to answer:\n{context}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += conversation_history[-10:]
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=1000,
        temperature=0.3
    )
    return response.choices[0].message.content