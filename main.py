#!/usr/bin/env python3
import time
import yaml
import schedule
from db import init_db
from lead_finder import find_leads
from emailer import email_leads
from reply_monitor import check_replies
from prototype import build_prototypes
from conversation import handle_conversation

with open('config.yaml') as f:
    config = yaml.safe_load(f)

def run_all():
    print("Running lead automation cycle...")
    find_leads()
    email_leads()
    check_replies()
    build_prototypes()
    handle_conversation()
    print("Cycle complete.\n")

def main():
    init_db()
    # Run immediately on start
    run_all()
    # Schedule recurring jobs
    schedule.every(config['intervals']['find_leads']).seconds.do(find_leads)
    schedule.every(config['intervals']['send_emails']).seconds.do(email_leads)
    schedule.every(config['intervals']['check_replies']).seconds.do(check_replies)
    schedule.every(config['intervals']['generate_prototype']).seconds.do(build_prototypes)
    schedule.every(config['intervals']['converse']).seconds.do(handle_conversation)
    print("Lead automation scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
