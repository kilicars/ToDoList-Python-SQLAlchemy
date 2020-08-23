from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

Base = declarative_base()


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())


class DbEngine:
    def __init__(self, db_name):
        engine = create_engine(f"sqlite:///{db_name}?check_same_thread=False")
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

    def create_task(self, task):
        self.session.add(task)
        self.session.commit()

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        self.session.delete(task)
        self.session.commit()

    def get_task_by_id(self, task_id):
        task = self.session.query(Task).filter(Task.id == task_id).all()[0]
        return task

    def get_tasks_by_date(self, day, is_late=False):
        if is_late:
            tasks = self.session.query(Task).filter(Task.deadline < day).all()
        else:
            tasks = self.session.query(Task).filter(Task.deadline == day).all()
        return tasks

    def get_all_tasks(self):
        tasks = self.session.query(Task).order_by(Task.deadline).all()
        return tasks


class ToDoList:

    def __init__(self):
        self.db = DbEngine("todo.db")
        self.today = datetime.today().date()
        self.show_menu = True
        self.main_menu()

    @staticmethod
    def print_menu():
        print("1) Today's tasks")
        print("2) Week's tasks")
        print("3) All tasks")
        print("4) Missed tasks")
        print("5) Add task")
        print("6) Delete task")
        print("0) Exit")

    def add_task(self):
        task = input("Enter task\n")
        deadline = datetime.strptime(input("Enter deadline"), "%Y-%m-%d")
        self.db.create_task(Task(task=task, deadline=deadline))
        print("The task has been added!\n")

    def delete_task(self):
        print("Choose the number of the task you want to delete:")
        tasks = self.db.get_all_tasks()
        self.print_tasks(tasks, None, None)
        task_no = int(input())
        task_id = tasks[task_no - 1].id
        self.db.delete_task(task_id)
        print("The task has been deleted!")

    def tasks_of_day(self, day, is_weekly=False):
        tasks = self.db.get_tasks_by_date(day)
        print_day = "Today"
        if is_weekly:
            print_day = day.strftime('%A')
        print(f"{print_day} {day.day} {day.strftime('%b')}")
        if len(tasks) == 0:
            print("Nothing to do!\n")
        else:
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.task}")
            print()

    def tasks_of_week(self):
        for i in range(0, 7):
            day = self.today + timedelta(i)
            self.tasks_of_day(day, is_weekly=True)

    def list_all_tasks(self):
        tasks = self.db.get_all_tasks()
        self.print_tasks(tasks, "All tasks", "Nothing to do!\n")

    def missed_tasks(self):
        missed_tasks = self.db.get_tasks_by_date(self.today, is_late=True)
        self.print_tasks(missed_tasks, "Missed tasks", "Nothing is missed\n")

    @staticmethod
    def print_tasks(tasks, header, empty_message):
        if header:
            print(header)
        if len(tasks) == 0:
            print(empty_message)
        else:
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.task}. {task.deadline.day} {task.deadline.strftime('%b')}")
            print()

    def quit(self):
        self.show_menu = False
        print("Bye")

    def main_menu(self):
        while self.show_menu:
            self.print_menu()
            choice = int(input())
            if choice == 1:
                self.tasks_of_day(self.today)
            elif choice == 2:
                self.tasks_of_week()
            elif choice == 3:
                self.list_all_tasks()
            elif choice == 4:
                self.missed_tasks()
            elif choice == 5:
                self.add_task()
            elif choice == 6:
                self.delete_task()
            elif choice == 0:
                self.quit()
            else:
                print("Invalid option")


todo_list = ToDoList()
