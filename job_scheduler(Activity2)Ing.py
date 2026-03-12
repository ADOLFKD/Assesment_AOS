import os
import time
from datetime import datetime
from collections import deque

jobs_file = "job_queue.txt"
completed_jobs_file = "completed_jobs.txt"
program_log_file = "scheduler_log.txt"

quantum_seconds = 5


#################
# Event Log
#################

def log_event(event, student_id, job_name, process):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    line = f"{timestamp}, {event}, {student_id}, {job_name}, {process}\n"
    with open(program_log_file, "a") as f:
        f.write(line)


#################
# File Functions
#################

def load_jobs():
    jobs = []
    if os.path.exists(jobs_file):
        with open(jobs_file, "r") as pending:
            for line in pending:
                line = line.strip()
                if line == "":
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 4:
                    continue

                student_id, job_name, exec_time, priority = parts
                try:
                    exec_time = int(exec_time)
                    priority = int(priority)
                except ValueError:
                    continue

                jobs.append({
                    "student_id": student_id,
                    "job_name": job_name,
                    "exec_time": exec_time,
                    "priority": priority
                })

    return jobs


def save_jobs(jobs):
    with open(jobs_file, "w") as f:
        for job in jobs:
            f.write(f"{job['student_id']},{job['job_name']},{int(job['exec_time'])},{int(job['priority'])}\n")


def save_completed_job(job, process):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(completed_jobs_file, "a") as f:
        f.write(f"{timestamp} | STUDENT ID: {job['student_id']} | JOB: {job['job_name']} | {process} | COMPLETED\n")


def submit_new_job():
    print("\n=== Submit New Job ===")

    # Validate student ID
    while True:
        student_id = input("Enter Student ID: ").strip()
        if student_id == "":
            print("Student ID cannot be empty")
        elif "," in student_id:
            print("Student ID cannot contain commas")
        else:
            break

    # Validate job name
    while True:
        job_name = input("Enter Job Name: ").strip()
        if job_name == "":
            print("Job Name cannot be empty")
        elif "," in job_name:
            print("Job Name cannot contain commas")
        else:
            break

    # Validate execution time
    while True:
        exec_time_input = input("Enter Execution Time in Seconds: ").strip()
        try:
            exec_time = int(exec_time_input)
            if exec_time > 0:
                break
            else:
                print("Execution time must be greater than 0")
        except ValueError:
            print("Invalid input")

    # Validate priority
    while True:
        priority_input = input("Enter Priority (1-10): ").strip()
        try:
            priority = int(priority_input)
            if 1 <= priority <= 10:
                break
            else:
                print("Priority must be between 1 and 10")
        except ValueError:
            print("Invalid input")

    # Load current jobs
    jobs = load_jobs()

    # Create new job
    jobs.append({
        "student_id": student_id,
        "job_name": job_name,
        "exec_time": exec_time,
        "priority": priority
    })

    # Save new job
    save_jobs(jobs)
    log_event("JOB SUBMITTED", student_id, job_name, "SUBMISSION")
    print("Job added to queue")


def view_pending_jobs():
    jobs = load_jobs()
    print("\n=== Pending Jobs ===")
    if jobs == []:
        print("No pending jobs")
        return
    for num, row in enumerate(jobs, start=1):
        print(f"{num}. ID: {row['student_id']} | Job: {row['job_name']} | Time: {row['exec_time']}s | Priority: {row['priority']}")


def view_completed_jobs():
    print("\n=== Completed Jobs ===")
    if os.path.exists(completed_jobs_file):
        with open(completed_jobs_file, "r") as f:
            content = f.read().strip()

        if content == "":
            print("No completed jobs")
        else:
            print(content)
    else:
        print("No completed jobs file yet")
        return


#################
# Round Robin
#################

def round_robin():
    jobs = load_jobs()
    print("\n=== Round Robin Processing ===")
    print(f"Quantum = {quantum_seconds}s")

    if jobs == []:
        print("No pending jobs")
        return

    # Process in arrival order
    queue = deque(jobs)
    turn = 0

    while queue:
        turn += 1
        job = queue.popleft()

        student_id = job.get("student_id")
        name = job.get("job_name")
        try:
            remaining = int(job["exec_time"])
        except Exception:
            remaining = 0

        if remaining <= 0:
            log_event("SKIP INVALID TIME", student_id, name, "ROUND ROBIN")
            print(f"[{turn}] | ID: {student_id} | Job: {name} | Remaining: {remaining}")
            save_completed_job(job, "ROUND ROBIN")
            save_jobs(list(queue))
            continue

        quantum = quantum_seconds if remaining > quantum_seconds else remaining
        current = remaining
        log_event(f"EXECUTION STARTED quantum: {quantum} remaining: {current}", student_id, name, "ROUND ROBIN")
        remaining -= quantum
        job["exec_time"] = remaining
        log_event(f"EXECUTION ENDED quantum: {quantum} remaining: {remaining}", student_id, name, "ROUND ROBIN")

        if remaining > 0:
            queue.append(job)
            action = "REQUEUE"
        else:
            log_event("JOB COMPLETED", student_id, name, "ROUND ROBIN")
            save_completed_job(job, "ROUND ROBIN")
            action = "COMPLETED"

        save_jobs(list(queue))
        print(f"[{turn}] RUN  | ID: {student_id} | JOB: {name} | {current} - {remaining} | {action} | In Queue: {len(queue)}")

    print("Jobs processed")


########################
# Priority Scheduling
########################

def priority_scheduling():
    jobs = load_jobs()

    print("\n=== Priority Scheduling Processing ===")

    if jobs == []:
        print("No pending jobs")
        return

    def get_priority(job):
        return int(job.get("priority", 0))

    # Sort by priority
    pending = sorted(jobs, key=get_priority, reverse=True)
    turn = 0

    while pending:
        turn += 1
        job = pending.pop(0)

        student_id = job.get("student_id")
        name = job.get("job_name")
        prio = job.get("priority")

        try:
            exec_time = int(job.get("exec_time", 0))
        except Exception:
            exec_time = 0

        if exec_time <= 0:
            log_event("SKIP INVALID TIME", student_id, name, "PRIORITY SCHEDULING")
            print(f"[{turn}] | ID: {student_id} | Job: {name} | Priority: {prio} | Time: {exec_time}")

            save_completed_job(job, "PRIORITY SCHEDULING")
            save_jobs(pending)
            continue

        log_event(f"EXECUTION STARTED priority: {prio} time: {exec_time}", student_id, name, "PRIORITY SCHEDULING")
        print(f"[{turn}] RUN  | ID: {student_id} | JOB: {name} | priority: {prio} | time: {exec_time}s")

        job["exec_time"] = 0
        save_completed_job(job, "PRIORITY SCHEDULING")

        log_event(f"EXECUTION ENDED, ran: {exec_time}", student_id, name, "PRIORITY SCHEDULING")
        log_event("JOB COMPLETED", student_id, name, "PRIORITY SCHEDULING")

        save_jobs(pending)
        
    print("Jobs processed")


################
# MENU
################

def main_menu():
    while True:
        print("\n=== Job Scheduler ===")
        print("1. View Pending Jobs")
        print("2. Submit Job Request")
        print("3. Process Job Queue (Round Robin)")
        print("4. Process Job Queue (Priority)")
        print("5. View Completed Jobs")
        print("6. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            view_pending_jobs()
        elif choice == "2":
            submit_new_job()
        elif choice == "3":
            round_robin()
        elif choice == "4":
            priority_scheduling()
        elif choice == "5":
            view_completed_jobs()
        elif choice == "6":
            while True:
                exit_choice = input("Are you sure you want to exit? (Y/N): ").strip().upper()
                if exit_choice == "Y":
                    return
                elif exit_choice == "N":
                    print("Exit cancelled")
                    break
                else:
                    print("Invalid option. Please enter Y or N")
        else:
            print("Invalid Option")


main_menu()