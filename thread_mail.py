import hashlib
import re
import shutil
import threading
import time

def process_logs(logs):
    global num_new_logs
    updated_logs = []  # List to store the updated log lines
    for line in logs:
        matches = re.findall(r'[<\"](\S+@\S+)[>\"]', line)
        for mail_id in matches:
            prefix = mail_id[:2]
            domain = extract_root_domain(mail_id)
            hashed_mail_id = hashlib.sha256(mail_id.encode()).hexdigest()[:64]
            updated_line = line.replace(mail_id, f"{prefix}_{hashed_mail_id}@{domain}")
            updated_logs.append(updated_line)  # Store the updated line
            num_new_logs += 1  # Increment the count of new logs

    # Overwrite the replace2.log file with the processed logs
    with open('/root/replace2.log', 'w') as file:
        file.writelines(updated_logs)

def extract_root_domain(email):
    parts = email.split('@')
    domain_parts = parts[1].split('.')
    if len(domain_parts) > 1:
        return domain_parts[-2] + '.' + domain_parts[-1]
    return parts[1]

def copy_logs():
    backup_file_name = f"/root/replace2_backup.log"
    shutil.copyfile('/root/replace2.log', backup_file_name)
    while True:
        # Copy the replace2.log file every 24 hours
        current_time = time.localtime()
        if current_time.tm_hour == 0 and current_time.tm_min == 0:
            backup_file_name = f"/root/replace2_backup.log"
            shutil.copyfile('/root/replace2.log', backup_file_name)

        time.sleep(60)

def monitor_logs():
    global num_new_logs
    last_position = 0
    while True:
        # Read the entire replace2.log file initially
        with open('/root/replace2.log', 'r') as file:
            logs = file.readlines()

        if num_new_logs > len(logs):
            num_new_logs = len(logs)  # Reset num_new_logs if logs are removed externally

        # Process all logs and overwrite the replace2.log file
        process_logs(logs)

        # Move the file pointer to the end of the file
        with open('/root/replace2.log', 'r') as file:
            file.seek(0, 2)
            last_position = file.tell()

        while True:
            # Read new logs and append them to the existing processed logs
            with open('/root/replace2.log', 'r') as file:
                file.seek(last_position)
                new_logs = file.readlines()
                if not new_logs:
                    break

            process_logs(new_logs)  # Process the new logs

            # Move the file pointer to the end of the file
            with open('/root/replace2.log', 'r') as file:
                file.seek(0, 2)
                last_position = file.tell()

        time.sleep(60)

num_new_logs = 0

# Start the monitor_logs thread
monitor_thread = threading.Thread(target=monitor_logs)
monitor_thread.start()

# Start the copy_logs thread
copy_thread = threading.Thread(target=copy_logs)
copy_thread.start()

# Wait for the monitor_logs thread to finish
monitor_thread.join()
