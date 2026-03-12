# System Utility & Security Toolkit

This repository contains a collection of professional-grade tools for system administration, process scheduling, and secure file management, implemented using **Bash** and **Python**.

---

## 🚀 Project Modules

### 1. System Administration Tool
An interactive Bash script designed for real-time monitoring and automated maintenance.
* **Resource Monitoring**: Calculates current CPU and Memory usage percentages.
* **Process Management**: Displays the top 10 memory-consuming processes and allows users to terminate specific PIDs.
* **Safety Protocols**: Blocks attempts to terminate critical system processes like `PID 1`, `systemd`, or `init`.
* **Smart Log Archiving**: Searches for `.log` files larger than 50MB, compresses them with `gzip`, and moves them to an `ArchiveLogs` folder.
* **Disk Alerts**: Issues a warning if the compressed logs directory exceeds 1GB.

### 2. Multi-Policy Job Scheduler
A Python-based simulation of operating system task management with persistent queue handling.
* **Round Robin (RR)**: Processes tasks using a circular queue with a 5-second time quantum.
* **Priority Scheduling**: Sorts and executes jobs based on a user-defined priority scale (1-10).
* **Input Validation**: Ensures Student IDs and Job Names do not contain commas and that execution times are valid integers.
* **Persistence**: Saves the state of pending jobs to `job_queue.txt` and logs all completed tasks.

### 3. Secure Submission System
A secure, two-tier architecture (Bash UI and Python Backend) for file handling and access control.
* **Cryptographic Integrity**: Uses **SHA-256 hashing** to identify and block duplicate file content or duplicate filenames in the registry.
* **Strict Validation**: Only allows `.pdf` and `.docx` formats with a maximum file size of 5MB.
* **Brute-Force Protection**: Implements a lockout mechanism that freezes accounts for 180 seconds after 3 failed login attempts.
* **Anomaly Detection**: Flags "suspicious activity" if multiple login attempts occur within a 60-second window.
* **Audit Trail**: Maintains a central `submission_log.txt` for all system events, status updates, and user activity.

---

## 🛠️ Installation & Setup

### Prerequisites
* **Linux/Unix** environment (or WSL)
* **Python 3.x**
* **Bash 4.0+**

### Permissions
Before running the shell scripts, ensure they have execution permissions:
```bash
chmod +x "admin_system_tool(Activity1)Ing.sh"
chmod +x "system_menu(Activity3).sh"
```
---

## 📂 Usage Guide

### System Administration
```bash
./"admin_system_tool(Activity1)Ing.sh"
```

### Job Scheduling
```bash
python3 "job_scheduler(Activity2)Ing.py"
```

### Secure Submission System
```bash
./"system_menu(Activity3).sh"
```

---

## 📋 File Registry & Logs

* `submission_registry.txt`: Database of unique file hashes.
* `access_control.txt`: Stores user attempt counts and lockout timestamps.
* `system_monitor_log.txt`: Logs all administrative actions and process terminations.
* `scheduler_log.txt`: Detailed event log for all job scheduling activities.
