from app import db,app
from flask_login import UserMixin
from flask import Flask
import flask_whooshalchemy as wa





follow_table = db.Table('followers',
    db.Column('user-id',db.Integer,db.ForeignKey('user.id')),
    db.Column('blog-id',db.Integer,db.ForeignKey('blog.id'))
)

likers = db.Table('likers',
    db.Column('user-id',db.Integer,db.ForeignKey('user.id')),
    db.Column('post-id',db.Integer,db.ForeignKey('posts.id'))
)

class User(UserMixin,db.Model):
    id =db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(15),unique=True)
    password=db.Column(db.String(80))
    email=db.Column(db.String(50),unique=True)
    blogs=db.relationship("Blog",backref='user',lazy=True)
    followed_blogs=db.relationship('Blog',secondary=follow_table,backref=db.backref('user_followers',lazy='dynamic'), lazy='dynamic')
    liked_posts=db.relationship('Posts',secondary=likers,backref=db.backref('user_likes',lazy='dynamic'), lazy='dynamic')
    def has_followed_blog(self, blog):
        return self.followed_blogs.filter_by(
          id=blog.id).first() is not None
    def has_liked_post(self, posts):
        return self.liked_posts.filter_by(
          id=posts.id).first() is not None

class Blog(db.Model):
    __searchable__ = ['blog_name']
    id= db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(100))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    posts=db.relationship("Posts",backref='blog',lazy=True)

    
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(500))
    body= db.Column(db.String(2000))
    author = db.Column(db.String(20))
    image_name=db.Column(db.String(100))
    blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    
   
    
    
