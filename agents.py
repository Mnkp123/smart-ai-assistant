from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME
from chat_engine import get_ai_response
import json

client = Groq(api_key=GROQ_API_KEY)

class PlannerAgent:
    def plan(self, user_message):
        prompt = f"""You are a planner. Analyze this message and decide action.
        
User message: "{user_message}"

Reply ONLY with this JSON, nothing else:
{{"action": "answer_question", "reason": "needs answer"}}

Action must be one of: answer_question, capture_lead, general_chat"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        try:
            text = response.choices[0].message.content
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            return {"action": "general_chat", "reason": "default"}

class ExecutorAgent:
    def execute(self, plan, user_message, rag_system, conversation_history):
        action = plan.get("action", "general_chat")
        if action == "answer_question":
            context = rag_system.retrieve(user_message)
            response = get_ai_response(user_message, conversation_history, context)
            return response, context
        else:
            response = get_ai_response(user_message, conversation_history)
            return response, ""

class ValidatorAgent:
    def validate(self, response, context):
        if not context:
            return True, "No context"
        return True, "Valid"