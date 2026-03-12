import os
import sys
import hashlib
from pathlib import Path
import time
from datetime import datetime

log_file = "submission_log.txt"
file_registry = "submission_registry.txt"
access_control = "access_control.txt"

max_size = 5
max_attempts = 3
threshold = 60  

##################################
# Event Logging
##################################

def log_event(event, student_id, file, status):
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # variable to avoid breaking the line
    file = file if file else "N/A"

    line = f"{date} | STUDENT ID: {student_id} | FILE: {file} | STATUS: {status} | EVENT: {event}\n"
    
    try:
        with open(log_file, "a") as f:
            f.write(line)
    except IOError as e:
        print(f"System Error: {e}")

#####################################
# Hashing and File Functions
#####################################  

def calculate_hash(file_path):
    try:
        return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
    except FileNotFoundError:
        return None

def validate_file(file_path):
    # Check if the file path exists
    if os.path.exists(file_path):
        # Check file extension
        extension = os.path.splitext(file_path)[1]
        if extension.lower() in ['.pdf', '.docx']:

            # Check file size
            size = os.path.getsize(file_path) / (1024 * 1024)
            
            if size <= max_size:
                return True, ""
            else:
                return False, f"File too large ({size:.2f}MB). Limit is {max_size}MB"
        else:
            return False, "Invalid file format. Only .pdf and .docx are allowed"
    else:
        return False, "File does not exist"
    
def check_duplicate(new_hash, file_name):
    base_name = os.path.basename(file_name)

    # Check if the file registry exists and load stored submissions
    if os.path.exists(file_registry):
        with open(file_registry, "r") as f:
            lines = f.read().splitlines()

        for line in lines:
            parts = line.split(" | ")
            if len(parts) == 2:
                stored_hash, stored_name = parts
                
                # Check if filename and content are duplicated
                if new_hash == stored_hash and base_name == stored_name:
                    return True, "Duplicated filename and content"
                elif new_hash == stored_hash:
                    return True, "Duplicated content"
                elif base_name == stored_name:
                    return True, "Duplicated filename"
                    
        return False, ""
    else:
        return False, ""

def save_submission_data(new_hash, file_name):
    base_name = os.path.basename(file_name)
    with open(file_registry, "a") as f:
        f.write(f"{new_hash} | {base_name}\n")

########################
# Access Control and Login
########################

def get_user_data(student_id):
    student_id = str(student_id).strip()

    attempts = 0
    unlock_time = 0.0
    last_attempt = 0.0

    if os.path.exists(access_control):
        with open(access_control, "r") as f:
            for line in f:
                parts = line.strip().split("|")

                # Expected format
                if len(parts) != 4:
                    continue

                user_id, attempts_str, unlock_time_str, last_attempt_str = parts
                user_id = user_id.strip()

                if user_id == student_id:
                    try:
                        attempts = int(attempts_str)
                        unlock_time = float(unlock_time_str)
                        last_attempt = float(last_attempt_str)
                    except ValueError:
                        attempts = 0
                        unlock_time = 0.0
                        last_attempt = 0.0
                    break

    return attempts, unlock_time, last_attempt

def update_user(student_id, attempts, unlock_time, last_attempt):
    lines = []
    user_found = False

    if os.path.exists(access_control):
        with open(access_control, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 4:
                    user_id = parts[0]
                    if user_id == student_id:
                        lines.append(f"{student_id}|{attempts}|{unlock_time}|{last_attempt}\n")
                        user_found = True
                    else:
                        lines.append(line)     
    if not user_found:
        lines.append(f"{student_id}|{attempts}|{unlock_time}|{last_attempt}\n")  

    with open(access_control, "w") as f:
        f.writelines(lines)  

def process_access(student_id, successful):
    current_time = time.time()
    attempts, unlock_time, last_attempt = get_user_data(student_id)

    # Check remaining lock time
    if current_time < unlock_time:
        remaining = int(unlock_time - current_time)
        log_event("LOGIN BLOCKED", student_id, None, "LOCKED")
        return 1, f"Account locked. Please wait {remaining} seconds"

    # Verify activity < 60s
    suspicious = (last_attempt > 0 and (current_time - last_attempt) < threshold)
    if suspicious:
        log_event("SUSPICIOUS ACTIVITY", student_id, None, "WARNING")

    if successful:
        # Reset counters if access is correct
        update_user(student_id, 0, 0.0, current_time)
        log_event("LOGIN SUCCESS", student_id, None, "SUCCESS")
        msg = "Login successful"
        if suspicious:
            msg = f"WARNING (<{threshold}s): suspicious activity detected. " + msg
        return 0, msg
    else:
        attempts = attempts + 1
       
        # Lock account
        if attempts >= max_attempts:
            unlock_account_time = current_time + 180 # Lock for 3min
            update_user(student_id, 0, unlock_account_time, current_time)
            log_event("ACCOUNT LOCKOUT", student_id, None, "LOCKED")
            return 1, "Account locked. Many failed attempts"
        else:
            # Count failures
            update_user(student_id, attempts, 0.0, current_time)
            log_event("LOGIN FAILED", student_id, None, "FAILED")
            return 1, f"Login failed. Attempts left: {max_attempts - attempts}"
        
#######################
# Main Execution
#######################

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Error: Missing arguments")
        sys.exit(1)
        

    command = sys.argv[1]

    if command == "submit":
        if len(sys.argv) != 4:
            print("Error: Invalid arguments for submit")
            sys.exit(1)
            
        student_id = sys.argv[2].strip()
        file = sys.argv[3]

        # Validate File Format and Size
        is_valid, message = validate_file(file)
        if not is_valid:
            print(message)
            log_event("ASSIGNMENT REJECTED", student_id, file, "INVALID FORMAT/SIZE")
            sys.exit(1)

        # Calculate Hash
        file_hash = calculate_hash(file)
        if file_hash is None:
            print("Error reading file")
            sys.exit(1)


        # Check Duplicates
        duplicate_found, error_reason = check_duplicate(file_hash, file)
        
        if duplicate_found:
            print(f"Error: {error_reason} detected")
            log_event("ASSIGNMENT REJECTED", student_id, file, error_reason.upper())
            sys.exit(1)

        # Upload File
        save_submission_data(file_hash, file) 
        log_event("ASSIGNMENT ACCEPTED", student_id, file, "SUCCESS")
        print("Assignment submitted successfully")
        sys.exit(0)

    elif command == "login":
        # Simulate a login attempt
        if len(sys.argv) != 4:
            print("Error: Invalid arguments for login")
            sys.exit(1)

        student_id = sys.argv[2].strip()
        simulated_status = sys.argv[3].lower()
        success = True if simulated_status == "success" else False
        
        code, message = process_access(student_id, success)
        print(message)
        sys.exit(code)

    elif command == "list_logs":
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                print(f.read())
        else:
            print("No logs available")
            sys.exit(0)
    else:
        print("Unknown command")
        sys.exit(1)