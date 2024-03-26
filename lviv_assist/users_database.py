"""
Simplify the process of finding and hiring service providers for various tasks and 
services. It provides a seamless user experience with a simple interface for registering, 
searching, and selecting service providers.
"""
from flask import Flask, render_template
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///employee.db', echo=True)

Base = declarative_base()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

class Employee(Base):
    """
    Abstract base class representing an employee.
    """
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    description = Column(String)
    price = Column(String)

class VentilationCleaners(Employee):
    """
    Subclass of Employee, representing ventilation cleaners.
    """
    __tablename__ = 'ventilation_cleaners'

class PlumbingTechnicians(Employee):
    """
    Subclass of Employee, representing plumbing technicians.
    """
    __tablename__ = 'plumbing_technicians'

class FurnitureRepair(Employee):
    """
    Subclass of Employee, representing furniture repair specialists.
    """
    __tablename__ = 'furniture_repair'

class SecuritySystem(Employee):
    """
    Subclass of Employee, representing furniture repair specialists.
    """
    __tablename__ = 'security_system'

class Electricians(Employee):
    """
    Subclass of Employee, representing electricians.
    """
    __tablename__ = 'electricians'

class WindowDoorReplacement(Employee):
    """
    Subclass of Employee, representing specialists in window and door replacement.
    """
    __tablename__ = 'window_and_door_replacement'

class Landscape(Employee):
    """
    Subclass of Employee, representing landscape specialists.
    """
    __tablename__ = 'landscape'

class HeatingSystem(Employee):
    """
    Subclass of Employee, representing heating system specialists.
    """
    __tablename__ = 'heating_system'

class Cleaning(Employee):
    """
    Subclass of Employee, representing cleaning specialists.
    """
    __tablename__ = 'cleaning'

class RoofRepair(Employee):
    """
    Subclass of Employee, representing roof repair specialists.
    """
    __tablename__ = 'roof_repair'

class Other(Employee):
    """
    Subclass of Employee, representing other types of specialists.
    """
    __tablename__ = 'other'
    hashtag = Column(String)

Base.metadata.create_all(engine)

class Filter:
    """
    Class for filtering and adding new employees.
    """
    @staticmethod
    def add_hashtag_profile(name, surname, email, description, price, hashtag):
        """
        Add a new employee profile with specified hashtag.
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        if hashtag == 'VentilationCleaners':
            new_user = VentilationCleaners(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'PlumbingTechnicians':
            new_user = PlumbingTechnicians(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'FurnitureRepair':
            new_user = FurnitureRepair(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'SecuritySystem':
            new_user = SecuritySystem(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'Electricians':
            new_user = Electricians(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'WindowDoorReplacement':
            new_user = WindowDoorReplacement(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'Landscape':
            new_user = Landscape(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'HeatingSystem':
            new_user = HeatingSystem(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'Cleaning':
            new_user = Cleaning(name=name, surname=surname, \
email=email, description=description, price=price)
        elif hashtag == 'RoofRepair':
            new_user = RoofRepair(name=name, surname=surname, \
email=email, description=description, price=price)
        else:
            new_user = Other(name=name, surname=surname, email=email, \
description=description, price=price, hashtag=hashtag)
        session.add(new_user)
        session.commit()
        session.close()
        return new_user
class GetHashtags:
    """
    Class for retrieving hashtags.
    """
    @staticmethod
    def get_hashtags():
        """
        Retrieve hashtags from the database.
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        service_providers = session.query(Other).all()
        hashtags = [sp.hashtag for sp in service_providers if not sp.hashtag is None]
        session.close()
        return list(set(hashtags))

class ShowEmployees:
    """
    Class for retrieving and displaying employee data.
    """
    @staticmethod
    def get_employee(email, description):
        """
        Retrieve an employee based on email and description.
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        employee_classes= ['VentilationCleaners', 'PlumbingTechnicians', 'FurnitureRepair', \
'SecuritySystem', 'Electricians', 'WindowDoorReplacement', 'Landscape', 'HeatingSystem', \
'Cleaning', 'RoofRepair', 'Other']
        for employee_class in employee_classes:
            employee_table = globals().get(employee_class)
            if employee_table:
                sp = session.query(employee_table).filter(employee_table.email == email, \
employee_table.description==description).first()
                if sp:
                    session.close()
                    return sp
        return None

    @staticmethod
    def show_employees(hashtag):
        """
        Show employees based on the specified hashtag.
        """
        engine = create_engine('sqlite:///employee.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        employee_class = globals().get(hashtag)

        if employee_class:
            service_providers = session.query(employee_class).all()
            employees_data = [{
            'name': sp.name,
            'surname': sp.surname,
            'email': sp.email,
            'description': sp.description,
            'price': sp.price,
        } for sp in service_providers]
            session.close()

            if employees_data:
                return render_template("search_employee.html", employees=employees_data)

        other_table = globals().get('Other')
        if other_table:
            service_providers = session.query\
(other_table).filter(other_table.hashtag == hashtag).all()
            employees_data = [{
                'name': sp.name,
                'surname': sp.surname,
                'email': sp.email,
                'description': sp.description,
                'price': sp.price,
            } for sp in service_providers]
            session.close()

            if employees_data:
                return render_template("search_employee.html", employees=employees_data)
        if hashtag is None:
            return render_template("index_search.html", hashtags=GetHashtags.get_hashtags())
        alert_script = f'''
            <script>
            window.onload = function() {{
                alert("Unfortunately, we are still searching for employees that \
could fulfill your request for {hashtag}");
            }}
            </script>
            '''
        return render_template("index_search.html", hashtags=GetHashtags.\
get_hashtags(), alert_script=alert_script)

if __name__ == "__main__":
    app.run(debug=True)
