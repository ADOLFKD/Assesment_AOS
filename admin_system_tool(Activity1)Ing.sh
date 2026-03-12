#!/bin/bash

log_file="system_monitor_log.txt"

log() {
	echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
}

#######################
# PROCESS MONITORING
#######################

monitor_processes() {

echo ""
echo "=== PROCESS MONITORING MODULE ==="

cpu_usage=$(top -bn1 | awk '/Cpu\(s\)/ {printf "%.2f", 100-$8}')
mem_usage=$(free | awk '/Mem:/ {printf "%.2f", $3/$2 *100}')

echo ""
echo "Current CPU Usage: $cpu_usage%"
echo "Current Memory Usage: $mem_usage%"

echo ""
echo "--- Top 10 Memory Consuming Processes ---"
ps -eo pid,user,%cpu,%mem,comm --sort=-%mem | head -n 11

echo ""
read -p "Enter PID to terminate: " pid

# If user enters nothing
if [[ -z "$pid" ]]; then
    	echo "No process selected"
    	return
fi

# Verify the process exists
if ! ps -p "$pid" > /dev/null 2>&1; then
    	echo "Process does not exist"
    	return
fi

# Block critical system process
if [[ "$pid" -eq 1 ]]; then
    	echo "Cannot terminate critical system process"
	return
fi

# Get process name
process_name=$(ps -p "$pid" -o comm=)

# Block critical processes by name
if [[ "$process_name" == "systemd" || "$process_name" == "init" ]]; then
	echo "Critical system process detected: $process_name"
	echo "Termination blocked"
	log "Blocked attempt to terminate critical process: $process_name (PID: $pid)"
	return
fi

# Confir process deletion
read -p "Are you sure you want to terminate PID $pid? (Y/N): " confirm

if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
    	kill "$pid" 2>/dev/null

    	if [[ $? -eq 0 ]]; then
        	echo "Process terminated successfully"
		log "Process terminated: PID $pid ($process_name)"
    	else
        	echo "Failed to terminate process"
    	fi
else
   	echo "Termination cancelled"
	log "Termination cancelled for PID $pid"
fi
}

######################
# PROCESS MONITORING
######################

inspect_disk() {

echo ""
echo "=== DISK INSPECTION AND LOG ARCHIVING ==="

read -p "Enter directory path to inspect: " dir

# Verify directory exists
if [[ ! -d "$dir" ]]; then
	echo "Directory does not exist"
	return
fi
# Check directory sizes
echo ""
echo "Disk usage for $dir:"
du -sh "$dir"

# Search for .log files larger than 50MB
echo ""
echo "Searching log files larger than 50MB"

large_logs=$(find "$dir" -type f -name "*.log" -size +50M)

if [[ -z "$large_logs" ]]; then
	echo "No large log files found"
else
	echo "Large log files detected:"
	echo "$large_logs"

	# Create ArchiveLogs directory
	mkdir -p ArchiveLogs
	echo "ArchiveLogs directory created"
	log "ArchiveLogs directory created"

	# Compress .log files
	for file in $large_logs; do
		timestamp=$(date "+%Y-%m-%d_%H%M%S")
		name=$(basename "$file")
		gzip -c "$file" > "ArchiveLogs/${name}_${timestamp}.gz"
		echo "$name has been archived in ArchiveLogs"
		log "$name has been archived in ArchiveLogs"
	done
fi

# Warn if ArchiveLogs > 1 GB
if [[ -d "ArchiveLogs" ]]; then
    size=$(du -sm "ArchiveLogs" | cut -f1)

    if [[ "$size" -gt 1024 ]]; then
        echo "WARNING: ArchiveLogs directory exceeds 1GB."
	log "ArchiveLogs exceeded 1GB"
    fi
fi

}

####################
# Close the program
####################
exit_program() {

echo ""
read -p "Are you sure you want to exit? (Y/N): " confirm

if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
    	log "Program exited by user"
    	exit 0
else
    	echo "Exit cancelled"
    	log "Exit attempt cancelled"
fi

}

####################
# Menu
####################

while true; do

echo ""
echo "===== SYSTEM ADMIN TOOL ====="
echo "1) Monitor Processes"
echo "2) Inspect Disk"
echo "3) Exit (Bye)"
echo "=============================="
echo ""
read -p "Select an option: " option

case $option in
	1) monitor_processes ;;
	2) inspect_disk ;;
	3) exit_program ;;
	*) echo "Invalid option. Please select 1, 2 or 3" ;;
esac

done