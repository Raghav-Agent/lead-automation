#!/usr/bin/env python3
from flask import Flask, send_from_directory, jsonify, render_template
from db import Session, Lead, init_db
from lead_finder import find_leads
from emailer import email_leads
from reply_monitor import check_replies
from prototype import build_prototypes
from conversation import handle_conversation
import os
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

app = Flask(__name__, static_folder='static', template_folder='templates')

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/leads')
def list_leads():
    session = Session()
    leads = session.query(Lead).all()
    result = []
    for l in leads:
        result.append({
            'id': l.id,
            'name': l.name,
            'email': l.email,
            'status': l.status,
            'prototype_url': l.prototype_url,
            'last_contacted': l.last_contacted.isoformat() if l.last_contacted else None
        })
    session.close()
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/admin/run/<step>')
def run_step(step):
    if step == 'find_leads':
        find_leads()
        return jsonify({'status': 'ran find_leads'})
    elif step == 'email_leads':
        email_leads()
        return jsonify({'status': 'ran email_leads'})
    elif step == 'check_replies':
        check_replies()
        return jsonify({'status': 'ran check_replies'})
    elif step == 'build_prototypes':
        build_prototypes()
        return jsonify({'status': 'ran build_prototypes'})
    elif step == 'converse':
        handle_conversation()
        return jsonify({'status': 'ran handle_conversation'})
    else:
        return jsonify({'error': 'unknown step'}), 400

@app.route('/admin/clear_leads', methods=['POST'])
def clear_leads():
    from db import Base, engine
    Base.metadata.drop_all(engine)
    init_db()
    return jsonify({'status': 'leads cleared'})

@app.route('/admin/generate_prototypes_for_selected', methods=['POST'])
def generate_prototypes_selected():
    from flask import request
    data = request.get_json()
    lead_ids = data.get('lead_ids', [])
    if not lead_ids:
        return jsonify({'error': 'lead_ids required'}), 400
    from prototype import build_prototypes
    # build_prototypes currently processes all leads with replied_yes and no prototype_url.
    # To limit to selected, we could modify it, but for now we just call it.
    build_prototypes()
    return jsonify({'status': 'prototype generation triggered', 'ids': lead_ids})

@app.route('/admin/send_emails_for_selected', methods=['POST'])
def send_emails_selected():
    from flask import request
    data = request.get_json()
    lead_ids = data.get('lead_ids', [])
    if not lead_ids:
        return jsonify({'error': 'lead_ids required'}), 400
    from emailer import send_initial_email
    session = Session()
    leads = session.query(Lead).filter(Lead.id.in_(lead_ids)).all()
    sent = []
    for lead in leads:
        if lead.email:
            send_initial_email(lead)
            sent.append(lead.id)
    session.close()
    return jsonify({'status': 'emails sent', 'sent_ids': sent})

@app.route('/admin/sales', methods=['POST'])
def run_sales():
    """
    Trigger a sales campaign.
    JSON body: { "niche": "dentists", "location": "New York, NY" }
    """
    from flask import request
    data = request.get_json()
    niche = data.get('niche')
    location = data.get('location')
    if not niche or not location:
        return jsonify({'error': 'niche and location required'}), 400
    from sales import run_sales_campaign
    # Run in background? For now, run synchronously (may take time)
    run_sales_campaign(niche, location)
    return jsonify({'status': 'campaign started', 'niche': niche, 'location': location})

@app.route('/admin/create_test_lead')
def create_test_lead():
    from datetime import datetime
    session = Session()
    lead = Lead(
        name='Test Co',
        email='test@example.com',
        source_url='https://test.com',
        niche=config['niche'],
        status='replied_yes',
        created_at=datetime.utcnow()
    )
    session.add(lead)
    session.commit()
    session.close()
    return jsonify({'status': 'created', 'id': lead.id})

@app.route('/admin/reset')
def reset_db():
    from db import Base, engine
    Base.metadata.drop_all(engine)
    init_db()
    return jsonify({'status': 'database reset'})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
