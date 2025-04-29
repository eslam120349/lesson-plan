from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    lessons = db.relationship('Lesson', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    teaching_strategy = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    generated_plan = db.Column(db.Text, nullable=True)
    gpt_plan = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    presentations = db.relationship('Presentation', backref='lesson', lazy='dynamic')
    
    def __repr__(self):
        return f'<Lesson {self.topic}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'grade_level': self.grade_level,
            'topic': self.topic,
            'teaching_strategy': self.teaching_strategy,
            'generated_plan': self.generated_plan,
            'gpt_plan': self.gpt_plan,
            'date_created': self.date_created.isoformat(),
            'date_modified': self.date_modified.isoformat(),
            'presentations': [p.to_dict() for p in self.presentations]
        }

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Presentation {self.id} for Lesson {self.lesson_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'file_path': self.file_path,
            'date_created': self.date_created.isoformat()
        }
