#!/bin/bash

set -u

# File Configuration
script="security(Activity3).py"
log_file="submission_log.txt"
file_registry="submission_registry.txt"

#######################
# Logging Function
#######################

log_message(){
    echo "$(date '+%d-%m-%Y %H:%M:%S') | SYSTEM INFO | EVENT: $1" >> "$log_file"
}

########################
# Check Dependency
########################

check_dependencies() {
    if [[ ! -f "$script" ]]; then
        echo "Error: '$script' not found"
        echo "Please make sure both files are in the same directory"
        exit 1
    fi
}

########################
# Submit Assignment
########################

submit_assignment() {

echo ""
echo "=== SUBMIT ASSIGNMENT MODULE ==="

read -p "Enter Student ID: " student_id
read -p "Enter Filename (.pdf/.docx): " file_name

if [[ -z "$file_name" ]]; then
    echo "Filename cannot be empty"
    return
fi

# Check if the file exists before sending it
if [[ ! -f "$file_name" ]]; then
    echo "File does not exist"
    return
fi

# Call python script
python3 "$script" submit "$student_id" "$file_name"

echo ""

}

########################
# Verify File
########################

verify_file() {

echo ""
echo "=== CHECK FILE STATUS ==="

read -p "Enter filename to check in registry: " check_file

if [[ -z "$check_file" ]]; then
    echo "Filename cannot be empty"
    return
fi

# Extract only the name
name=$(basename "$check_file")

echo "Checking registry for '$name'"

if [[ -f "$file_registry" ]]; then
    # Search for "file_name"
    if grep -q " | $name$" "$file_registry"; then
        echo "'$name' already exists in the registry"
    else
        echo "'$name' is not in the registry"
    fi
else
    echo "Registry file does not exist yet. No files have been submitted"
fi

echo ""

}

########################
# List Assignments
########################

list_assignments() {

echo ""
echo "=== SUBMITTED ASSIGNMENTS ==="

if [[ -f "$log_file" ]]; then
    assignments=$(grep "EVENT: ASSIGNMENT ACCEPTED" "$log_file" | grep "STATUS: SUCCESS" | sed 's/ | EVENT:.*$//' | sed 's/STATUS: SUCCESS/SUBMITTED/')

    if [[ -n "$assignments" ]]; then
        echo "$assignments"
    else
        echo "No submissions recorded yet"
    fi
else
    echo "No submissions recorded yet"
fi

echo ""

}

########################
# Simulate Login
########################

simulate_login() {    
    echo ""
    echo "=== LOGIN SIMULATION ==="
    read -p "Enter user: " user

    while true; do
        echo ""
        echo "User: $user"
        echo "1) Simulate Success"
        echo "2) Simulate Failure"
        echo "3) Back to main menu"
        read -p "Select option: " simulation_option

        case "$simulation_option" in
        1) python3 "$script" login "$user" success ;;
        2) python3 "$script" login "$user" fail ;;
        3) break ;;
        *) echo "Invalid option. Please enter 1, 2 or 3" ;;
        esac
    done
}

########################
# Exit Program
########################

exit_program() {

while true; do
    read -p "Are you sure you want to exit? (Y/N): " confirmation

    if [[ "$confirmation" == "Y" || "$confirmation" == "y" ]]; then
        log_message "Program exited by user"
        exit 0

    elif [[ "$confirmation" == "N" || "$confirmation" == "n" ]]; then
        echo "Exit cancelled"
        return

    else
        echo "Invalid option. Please enter Y or N"
    fi
done

}

########################
# Main Menu
########################

check_dependencies

while true; do

echo ""
echo "===== SECURE SUBMISSION SYSTEM ====="
echo "1) Submit Assignment"
echo "2) Check File Status"
echo "3) List Submitted Assignments"
echo "4) Simulate Login"
echo "5) Exit"
echo "===================================="
echo ""
read -p "Select an option: " option

case $option in 
    1) submit_assignment ;;
    2) verify_file ;;
    3) list_assignments ;;
    4) simulate_login ;;
    5) exit_program ;;
    *) echo "Invalid option. Please select 1-5" ;;
esac

done