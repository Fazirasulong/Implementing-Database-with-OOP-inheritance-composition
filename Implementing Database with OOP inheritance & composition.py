import sqlite3
from abc import ABC, abstractmethod

# Address class (Composition)
class Address:
    def __init__(self, street, city, state, zip_code):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code

# Abstract Employee class (Inheritance)
class Employee(ABC):
    def __init__(self, emp_id, name, address, emp_type):
        self.emp_id = emp_id
        self.name = name
        self.address = address
        self.emp_type = emp_type

    @abstractmethod
    def calculate_pay(self):
        pass

# Subclasses for different employee types
class SalariedEmployee(Employee):
    def __init__(self, emp_id, name, address, salary):
        super().__init__(emp_id, name, address, 'Salaried')
        self.salary = salary
    
    def calculate_pay(self):
        return self.salary

class HourlyEmployee(Employee):
    def __init__(self, emp_id, name, address, hourly_rate, hours_worked):
        super().__init__(emp_id, name, address, 'Hourly')
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked
    
    def calculate_pay(self):
        return self.hourly_rate * max(0, self.hours_worked)  # Prevent negative hours

class CommissionEmployee(Employee):
    def __init__(self, emp_id, name, address, base_salary, commission_rate, sales):
        super().__init__(emp_id, name, address, 'Commission')
        self.base_salary = base_salary
        self.commission_rate = commission_rate
        self.sales = sales
    
    def calculate_pay(self):
        return self.base_salary + (self.commission_rate * self.sales)

# Database setup
def setup_database():
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Address (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address_id INTEGER,
        name TEXT,
        emp_type TEXT,
        salary REAL,
        hourly_rate REAL,
        hours_worked REAL,
        base_salary REAL,
        commission_rate REAL,
        sales REAL,
        FOREIGN KEY(address_id) REFERENCES Address(id)
    )""")
    
    conn.commit()
    conn.close()

# Add employee to database
def add_employee(employee):
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO Address (street, city, state, zip_code) VALUES (?, ?, ?, ?)",
                   (employee.address.street, employee.address.city, employee.address.state, employee.address.zip_code))
    address_id = cursor.lastrowid
    
    cursor.execute("""
    INSERT INTO Employee (address_id, name, emp_type, salary, hourly_rate, hours_worked, base_salary, commission_rate, sales)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (address_id, employee.name, employee.emp_type,
     getattr(employee, 'salary', None),
     getattr(employee, 'hourly_rate', None),
     getattr(employee, 'hours_worked', None),
     getattr(employee, 'base_salary', None),
     getattr(employee, 'commission_rate', None),
     getattr(employee, 'sales', None)))
    
    conn.commit()
    conn.close()

# Retrieve employee by ID
def get_employee(emp_id):
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Employee WHERE id = ?", (emp_id,))
    employee = cursor.fetchone()
    conn.close()
    return employee

# Process payroll
def process_payroll():
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employee")
    employees = cursor.fetchall()
    
    report = "Payroll Report:\n"
    for emp in employees:
        emp_id, address_id, name, emp_type, salary, hourly_rate, hours_worked, base_salary, commission_rate, sales = emp
        
        if emp_type == 'Salaried':
            pay = salary
        elif emp_type == 'Hourly':
            pay = hourly_rate * max(0, hours_worked)
        elif emp_type == 'Commission':
            pay = base_salary + (commission_rate * sales)
        else:
            pay = 0
        
        report += f"{name} ({emp_type}) - Pay: ${pay:.2f}\n"
    
    print(report)
    with open("payroll_report.txt", "w") as file:
        file.write(report)
    conn.close()

# Initialize database
setup_database()

# Example usage
if __name__ == "__main__":
    addr1 = Address("354/2 BT", "Narathiwat", "Meang", "96000")
    addr2 = Address("354/1", "Pattani", "Takbai", "96001")
    
    emp1 = SalariedEmployee(None, "Royyim", addr1, 5000)
    emp2 = HourlyEmployee(None, "Ahlam", addr2, 20, 160)
    emp3 = CommissionEmployee(None, "Mirhan", addr1, 3000, 0.05, 20000)
    
    add_employee(emp1)
    add_employee(emp2)
    add_employee(emp3)
    
    process_payroll()