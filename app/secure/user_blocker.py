import datetime
import hashlib
import os
import json
from .deviceInfo import deviceID_selector

MAX_ATTEMPTS = 10
BLOCK_THRESHOLD = datetime.timedelta(hours=1)
JSON_FILE_PATH = 'device_entry.json'

# Load data from JSON file or create it if not found
def load_data():
    if os.path.exists(JSON_FILE_PATH) and os.path.getsize(JSON_FILE_PATH) > 0:
        with open(JSON_FILE_PATH, 'r') as json_file:
            return json.load(json_file)
    else:
        # Initialize empty structure if file is not found or is empty
        return {"logged_devices": [], "blocklist": []}

def save_data(data):
    with open(JSON_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# Find device by user
def find_device(user):
    data = load_data()
    for device in data['logged_devices']:
        if device['user'] == user:
            return device
    return None

# Check if user is blocked and remove if time exceeds the threshold
def is_blocked(user):
    current_time = datetime.datetime.now()
    data = load_data()
    existing_device = find_device(user)
    
    for device in data['blocklist']:
        if device['user'] == user:
            blocked_time = datetime.datetime.fromisoformat(device['blocked_datetime'])

            if current_time - blocked_time < BLOCK_THRESHOLD:
                return True
            else:
                data['blocklist'].remove(device)

                 # Save changes to JSON
                if existing_device:
                    for device in data['logged_devices']:
                        if device['user'] == existing_device['user']:
                            device['attempts'] = 0

                save_data(data)

    return False

# Limit the unsuccessful login attempts request of an IP address 
def loginAttempt(action, agent):
    user_info = deviceID_selector(agent)
    user = hashlib.sha256(user_info['ip_address'].encode()).hexdigest()
    existing_device = find_device(user)
    
    if is_blocked(user):
        print(user_info['ip_address'], "is currently blocked from making login attempts.")
        return
    
    data = load_data()
    
    if action == 'reset':
        if existing_device:
            for device in data['logged_devices']:
                if device['user'] == existing_device['user']:
                    device['attempts'] = 0
        else:
            data['logged_devices'].append({'user': user, 'attempts': 0})
    
    elif action == 'count':
        if existing_device:
            for device in data['logged_devices']:
                if device['user'] == existing_device['user']:
                    device['attempts'] += 1

                    # Check if attempts exceed MAX_ATTEMPTS
                    if device['attempts'] >= MAX_ATTEMPTS:
                        if not any(d['user'] == existing_device['user'] for d in data['blocklist']):
                            data['blocklist'].append({'user': existing_device['user'], 'blocked_datetime': datetime.datetime.now().isoformat()})                            
        else:
            data['logged_devices'].append({'user': user, 'attempts': 1}) 

    # Save changes to JSON after any updates
    save_data(data)

# Example usage
if __name__ == '__main__':
    loginAttempt('count')  # Simulate a login attempt
