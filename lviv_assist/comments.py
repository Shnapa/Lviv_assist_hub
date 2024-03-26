"""
This script defines classes and functions to manage comments in a Flask application.
"""
from flask import Flask
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

app = Flask(__name__)

engine = create_engine('sqlite:///comments.db', poolclass=QueuePool)

Base = declarative_base()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

class Comment(Base):
    """
    Represents a comment entity in the database.
    """
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    name_from = Column(String)
    name_to = Column(String)
    surname_to = Column(String)
    email_to = Column(String)
    description = Column(String)
    comment = Column(String)

class GetComments:
    """
    Provides functionality to retrieve comments from the database.
    """
    @staticmethod
    def get_comments(name_from, email_to, description):
        """
        Retrieves comments from the database based on specified criteria.
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        comments_table = session.query(Comment)
        if name_from is None:
            print(comments_table.filter(Comment.email_to == email_to,
                                        Comment.description == description).all())
            return comments_table.filter(Comment.email_to == email_to,
                                        Comment.description == description).all()
        comments = comments_table.filter(Comment.name_from == name_from,
                                        Comment.email_to == email_to,
                                        Comment.description == description).all()
        comments = [comment for comment in comments if comment.comment is not None]
        session.close()
        return comments

class AddComments:
    """
    Provides functionality to add comments to the database.
    """
    @staticmethod
    def add_comment(name_from, name_to, surname_to, email_to, description, comment):
        """
        Adds a new comment to the database.
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        existing_comments = GetComments.get_comments(name_from, email_to, description)
        for existing_comment in existing_comments:
            if existing_comment.comment == comment:
                session.close()
                return None
        new_comment = Comment(
            name_from=name_from,
            name_to=name_to,
            surname_to=surname_to,
            email_to=email_to,
            comment=comment,
            description = description
        )
        session.add(new_comment)
        session.commit()
        return new_comment

Base.metadata.create_all(engine)
