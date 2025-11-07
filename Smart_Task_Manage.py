import json
from datetime import datetime

FILENAME = "tasks.json"

def load_tasks():
    try:
        with open(FILENAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(FILENAME, "w") as f:
        json.dump(tasks, f, indent=2)

def show_tasks(tasks):
    if not tasks:
        print("\nNo tasks to display!\n")
        return
    print("\n==== Your Tasks ====")
    tasks = sorted(tasks, key=lambda x: (x["priority"], x["deadline"]))
    for i, t in enumerate(tasks, start=1):
        status = "Done" if t["done"] else "Pending"
        print(f"{i}. {t['title']} | Priority: {t['priority']} | Due: {t['deadline']} | {status}")
    print()
    input("Press Enter to return to menu...")

def add_task(tasks):
    title = input("Enter task name (or press Enter to skip): ").strip()
    if not title:
        print("No task entered! Nothing added.\n")
        return

    try:
        priority = int(input("Priority (1-High, 2-Medium, 3-Low): "))
        if priority not in [1, 2, 3]:
            print("Invalid priority! Must be 1, 2, or 3.")
            return
    except ValueError:
        print("Invalid input! Priority must be a number.")
        return

    deadline = input("Enter deadline (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format! Please use YYYY-MM-DD.")
        return

    task = {"title": title, "priority": priority, "deadline": deadline, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print("Task added successfully!\n")

def mark_done(tasks):
    tasks = load_tasks()
    if not tasks:
        print("No tasks to mark done!\n")
        return
    show_tasks(tasks)
    try:
        n = int(input("Enter task number to mark as done: "))
        if 1 <= n <= len(tasks):
            tasks[n - 1]["done"] = True
            save_tasks(tasks)
            print("Task marked as done!\n")
        else:
            print("Invalid task number!\n")
    except ValueError:
        print("Invalid input! Please enter a number.\n")

def remove_overdue(tasks):
    today = datetime.today().date()
    filtered = [
        t for t in tasks
        if datetime.strptime(t["deadline"], "%Y-%m-%d").date() >= today
    ]
    if len(filtered) != len(tasks):
        print("Removed overdue tasks.\n")
    save_tasks(filtered)
    return filtered

def display_menu():
    print("\n==== SMART TO-DO LIST ====")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task as Done")
    print("4. Exit")

def main():
    tasks = load_tasks()
    tasks = remove_overdue(tasks)

    while True:
        display_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            tasks = load_tasks()
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
            tasks = load_tasks()
        elif choice == "3":
            mark_done(tasks)
            tasks = load_tasks()
        elif choice == "4":
            print("Goodbye! Tasks saved successfully.")
            break
        elif choice == "":
            print("No input given.\n")
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
