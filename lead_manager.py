import json, os
from datetime import datetime
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)
LEADS_FILE = "leads.json"

def load_leads():
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leads(leads):
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def classify_lead(conversation_text):
    prompt = f"""
    Conversation analyze karo aur lead classify karo.
    Conversation: {conversation_text}
    
    Sirf JSON return karo:
    {{
        "temperature": "hot/warm/cold",
        "name": "name ya Unknown",
        "email": "email ya Unknown",
        "phone": "phone ya Unknown",
        "requirements": "kya chahiye briefly",
        "reason": "kyun ye temperature diya"
    }}
    Hot = Budget + Timeline + Decision maker
    Warm = Interest hai but abhi decide nahi
    Cold = Sirf information le raha hai
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    try:
        text = response.choices[0].message.content
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except:
        return {"temperature": "cold", "name": "Unknown",
                "email": "Unknown", "phone": "Unknown",
                "requirements": "Not captured", "reason": "Parse error"}

def save_lead(lead_data):
    leads = load_leads()
    lead_data['id'] = len(leads) + 1
    lead_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    leads.append(lead_data)
    save_leads(leads)
    return lead_data

def generate_followup_email(lead_data):
    prompt = f"""
    Lead ke liye professional follow-up email likho:
    Name: {lead_data.get('name', 'Customer')}
    Requirements: {lead_data.get('requirements', 'your inquiry')}
    Type: {lead_data.get('temperature', 'warm')}
    Short aur professional email likho.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content