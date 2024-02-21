# from flask import Flask, render_template, request

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template("index.html")

# @app.route("/login")
# def login():
#     return render_template("login.html")
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Post, Thing

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post, 'Thing': Thing}

