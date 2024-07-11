import datetime

logged_devices = []
blocklist = []
MAX_ATTEMPTS = 10
BLOCK_THRESHOLD = datetime.timedelta(hours=1) 

from .deviceInfo import getUserInfo

#get the user from the array
def find_device(user):
    for device in logged_devices:
        if device['user'] == user:
            return device
    return None

#determine if user is blocked and remove if time exceeds the threshold
def is_blocked(user):
    current_time = datetime.datetime.now()
    existing_device = find_device(user)
    for device in blocklist:
        if device['user'] == user:
            if current_time - device['blocked_datetime'] < BLOCK_THRESHOLD:
                return True
            else:
                blocklist.remove(device)
                if existing_device:
                    existing_device['attempts'] = 0
                return False
    return False

#limit the unsuccessful login attempts request of an ip address 
def loginAttempt(action):
    user_info = getUserInfo()
    ipaddress = user_info['ip_address']
    user = hashlib.sha256(ipaddress.encode()).hexdigest()
    existing_device = find_device(user)
    
    if is_blocked(user):
        print( ipaddress," is currently blocked from making login attempts.")
    
    else:
        if action == 'reset':
            if existing_device:
                existing_device['attempts'] = 0
            else:
                logged_devices.append({'user': user, 'attempts': 0})

        elif action == 'count':
            if existing_device:
                existing_device['attempts'] += 1
                if existing_device['attempts'] >= MAX_ATTEMPTS:
                    if not any(device['user'] == user for device in blocklist):
                        blocklist.append({'user': user, 'blocked_datetime': datetime.datetime.now()})
            else:
                logged_devices.append({'user': user, 'attempts': 1})