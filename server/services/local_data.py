import json
import os
import random

FACTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'facts.json')
TIPS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tips.json')

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def get_random_fact():
    facts = load_json(FACTS_FILE)
    return random.choice(facts)

def get_tip_for_state(state):
    tips = load_json(TIPS_FILE)
    state_tips = tips.get(state, tips['neutral'])
    return random.choice(state_tips)
