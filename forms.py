from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please choose another one.')

class LessonForm(FlaskForm):
    GRADE_CHOICES = [
        ('K', 'Kindergarten'),
        ('1', '1st Grade'),
        ('2', '2nd Grade'),
        ('3', '3rd Grade'),
        ('4', '4th Grade'),
        ('5', '5th Grade'),
        ('6', '6th Grade'),
        ('7', '7th Grade'),
        ('8', '8th Grade'),
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade'),
    ]

    STRATEGY_CHOICES = [
        ('cooperative_learning', 'Cooperative Learning'),
        ('brainstorming', 'Brainstorming'),
        ('discovery_learning', 'Discovery Learning'),
        ('direct_instruction', 'Direct Instruction'),
        ('project_based', 'Project-Based Learning'),
        ('flipped_classroom', 'Flipped Classroom'),
        ('inquiry_based', 'Inquiry-Based Learning'),
        ('differentiated_instruction', 'Differentiated Instruction'),
        ('game_based', 'Game-Based Learning')
    ]

    Lang=[
    ('English', 'English'),
    ('Arabic', 'Arabic')
    ]

    grade_level = SelectField('Grade Level', choices=GRADE_CHOICES, validators=[DataRequired()])
    topic = StringField('Lesson Topic', validators=[DataRequired(), Length(min=3, max=200)])
    language = SelectField('language', choices=Lang, validators=[DataRequired()])
    teaching_strategy = SelectField('Teaching Strategy', choices=STRATEGY_CHOICES, validators=[DataRequired()])
    submit = SubmitField('Generate Lesson Plan')

class EditLessonForm(FlaskForm):
    generated_plan = TextAreaField('Generated Plan', validators=[DataRequired()])
    gpt_plan = TextAreaField('GPT Plan', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class ARLessonForm(FlaskForm):
    GRADE_CHOICES = [
        ('K', 'الروضة'),
        ('1', 'الصف الأول'),
        ('2', 'الصف الثاني'),
        ('3', 'الصف الثالث'),
        ('4', 'الصف الرابع'),
        ('5', 'الصف الخامس'),
        ('6', 'الصف السادس'),
        ('7', 'الصف السابع'),
        ('8', 'الصف الثامن'),
        ('9', 'الصف التاسع'),
        ('10', 'الصف العاشر'),
        ('11', 'الصف الحادي عشر'),
        ('12', 'الصف الثاني عشر'),
    ]

    STRATEGY_CHOICES = [
        ('cooperative_learning', 'التعلم التعاوني'),
        ('brainstorming', 'العصف الذهني'),
        ('discovery_learning', 'التعلم بالاكتشاف'),
        ('direct_instruction', 'التعليم المباشر'),
        ('project_based', 'التعلم القائم على المشاريع'),
        ('flipped_classroom', 'الفصل المقلوب'),
        ('inquiry_based', 'التعلم القائم على الاستقصاء'),
        ('differentiated_instruction', 'التعليم المتمايز'),
        ('game_based', 'التعلم القائم على اللعب')
    ]

    topic = StringField('عنوان الدرس', validators=[DataRequired(), Length(min=3, max=200)])
    grade_level = SelectField('المستوى الدراسي', choices=GRADE_CHOICES, validators=[DataRequired()])
    teaching_strategy = SelectField('استراتيجية التدريس', choices=STRATEGY_CHOICES, validators=[DataRequired()])
    textbook_content = TextAreaField('محتوى الكتاب المدرسي', validators=[DataRequired(), Length(min=100)])
    submit = SubmitField('توليد خطة الدرس')

class UserProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
        validators=[Optional(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Save Changes')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please choose another one.')

class WhatsAppMessageForm(FlaskForm):
    excel_file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Excel files only!')
    ])
    grades_column = IntegerField('Grades Column Number', validators=[
        DataRequired(),
        NumberRange(min=1, message='Column number must be at least 1')
    ])
    phone_column = IntegerField('Phone Numbers Column Number', validators=[
        DataRequired(),
        NumberRange(min=1, message='Column number must be at least 1')
    ])
    student_name_column = IntegerField('Student Name Column Number', validators=[
        DataRequired(),
        NumberRange(min=1, message='Column number must be at least 1')
    ])
    message_template = TextAreaField('Message Template', validators=[
        DataRequired(),
        Length(min=10, max=1000)
    ], default="Dear Parent, your child {student_name} has received a grade of {grade}.")
    submit = SubmitField('Send Messages')
