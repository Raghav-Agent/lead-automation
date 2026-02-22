import openai
import yaml
import os
from db import Session, Lead
from datetime import datetime
import json

with open('config.yaml') as f:
    config = yaml.safe_load(f)

openai.api_key = os.getenv('OPENAI_API_KEY')

def get_ai_response(lead, user_message):
    # Build a conversation context
    history = lead.conversation_history or []
    # Add user message
    history.append({"role": "user", "content": user_message})
    # System prompt
    system = f"You are an AI assistant helping a lead interested in {config['niche']}. Be friendly, concise, and persuasive. Goal: move toward conversion."
    messages = [{"role": "system", "content": system}] + history
    try:
        response = openai.chat.completions.create(
            model=config['ai']['model'],
            messages=messages,
            max_tokens=256,
            temperature=0.7
        )
        ai_reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": ai_reply})
        # Update lead
        session = Session()
        lead_obj = session.query(Lead).filter_by(id=lead.id).first()
        if lead_obj:
            lead_obj.conversation_history = history
            if lead_obj.status == 'prototype_sent':
                lead_obj.status = 'in_conversation'
            session.commit()
        session.close()
        return ai_reply
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, I'm having trouble connecting right now."

def handle_conversation():
    session = Session()
    # Find leads in conversation or with prototype sent
    leads = session.query(Lead).filter(Lead.status.in_(['in_conversation', 'prototype_sent'])).all()
    for lead in leads:
        # In a real system, we'd fetch new incoming messages from email or chat
        # For demo, we'll just simulate: if last message is from user, we reply
        history = lead.conversation_history or []
        if history and history[-1]['role'] == 'user':
            reply = get_ai_response(lead, history[-1]['content'])
            print(f"Replied to lead {lead.id}: {reply}")
            # Here we would send the reply via email or chat
    session.close()

if __name__ == '__main__':
    handle_conversation()
