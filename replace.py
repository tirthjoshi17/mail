import hashlib
import re
import shutil
import time

def process_logs(start_line):
    global num_new_logs
    with open('/root/replace2.log', 'r') as file:
        logs = file.readlines()
    with open('/root/replace3.log', 'a') as file:
        for i in range(start_line, len(logs)):
            line = logs[i]
            matches = re.findall(r'[<\"](\S+@\S+)[>\"]', line)
            for mail_id in matches:
                prefix = mail_id[:2]
                domain = extract_root_domain(mail_id)
                hashed_mail_id = hashlib.sha256(mail_id.encode()).hexdigest()[:5]
                updated_line = line.replace(mail_id, f"{prefix}_{hashed_mail_id}@{domain}")
                file.write(updated_line)
        num_new_logs = len(logs)

def extract_root_domain(email):
    parts = email.split('@')
    domain_parts = parts[1].split('.')
    if len(domain_parts) > 1:
        return domain_parts[-2] + '.' + domain_parts[-1]
    return parts[1]

def monitor_logs():
    global num_new_logs
    while True:
        process_logs(num_new_logs)
        time.sleep(60)

num_new_logs = 0
monitor_logs()
