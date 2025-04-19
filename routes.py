import os
import tempfile
from flask import render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Lesson, Presentation
from forms import LoginForm, RegistrationForm, LessonForm, EditLessonForm, TextbookContentForm
from lesson_generator import generate_lesson_plan
from ppt_generator import create_presentation
from textbook_processor import process_textbook_content
from urllib.parse import urlparse

@app.route('/')
def index():
    return render_template('index_new.html')

@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        name=data.get('name'),
        email=data.get('email')
    )
    user.set_password(data.get('password'))
    
    # Save user to database
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'success': True, 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    
    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout_api():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/user')
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email
    })

@app.route('/api/lessons', methods=['GET'])
@login_required
def get_lessons():
    lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.date_modified.desc()).all()
    return jsonify([lesson.to_dict() for lesson in lessons])

@app.route('/api/lessons', methods=['POST'])
@login_required
def create_lesson():
    data = request.get_json()
    
    # Create new lesson
    lesson = Lesson(
        user_id=current_user.id,
        grade_level=data.get('grade_level'),
        topic=data.get('topic'),
        teaching_strategy=data.get('teaching_strategy')
    )
    
    # Generate lesson plan content
    try:
        lesson_plan = generate_lesson_plan(
            data.get('grade_level'),
            data.get('topic'),
            data.get('teaching_strategy')
        )
        lesson.generated_plan = lesson_plan
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating lesson plan: {str(e)}'}), 500
    
    # Save to database
    db.session.add(lesson)
    db.session.commit()
    
    return jsonify({'success': True, 'lesson': lesson.to_dict()})

@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if the lesson belongs to the current user
    if lesson.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    return jsonify(lesson.to_dict())

@app.route('/api/lessons/<int:lesson_id>', methods=['PUT'])
@login_required
def update_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if the lesson belongs to the current user
    if lesson.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    data = request.get_json()
    
    # Update lesson details
    if 'generated_plan' in data:
        lesson.generated_plan = data['generated_plan']
    
    # Save changes
    db.session.commit()
    
    return jsonify({'success': True, 'lesson': lesson.to_dict()})

@app.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson_api(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if the lesson belongs to the current user
    if lesson.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    # Delete associated presentations
    for presentation in lesson.presentations:
        db.session.delete(presentation)
    
    # Delete the lesson
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson plan deleted successfully')
    return redirect(url_for('get_lessons_page'))

@app.route('/api/lessons/<int:lesson_id>', methods=['DELETE'])
@login_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if the lesson belongs to the current user
    if lesson.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Delete associated presentations
    for presentation in lesson.presentations:
        db.session.delete(presentation)
    
    # Delete the lesson
    db.session.delete(lesson)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/lessons/<int:lesson_id>/presentation', methods=['POST'])
@login_required
def generate_presentation(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if the lesson belongs to the current user
    if lesson.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Create a temporary file for the presentation
    try:
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
            temp_filename = temp_file.name
            
        # Generate the presentation
        create_presentation(lesson.grade_level, lesson.topic, lesson.teaching_strategy, 
                          lesson.generated_plan, temp_filename)
        
        # Create presentation record
        presentation = Presentation(
            lesson_id=lesson_id,
            file_path=temp_filename
        )
        
        db.session.add(presentation)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'presentation_id': presentation.id,
            'message': 'Presentation generated successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating presentation: {str(e)}'}), 500

@app.route('/api/presentations/<int:presentation_id>/download', methods=['GET'])
@login_required
def download_presentation(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    lesson = Lesson.query.get_or_404(presentation.lesson_id)
    
    # Check if the presentation belongs to the current user
    if lesson.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    # Check if file exists
    if not os.path.exists(presentation.file_path):
        return jsonify({'success': False, 'message': 'Presentation file not found'}), 404
    
    # Generate filename
    filename = f"Lesson_{lesson.topic.replace(' ', '_')}.pptx"
    
    # Send the file
    return send_file(
        presentation.file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )

# Regular form-based routes (optional, for initial render)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        flash('Invalid email or password')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's lessons
    total_lessons = Lesson.query.filter_by(user_id=current_user.id).count()
    recent_lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.date_modified.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          total_lessons=total_lessons,
                          recent_lessons=recent_lessons)

@app.route('/lessons')
@login_required
def get_lessons_page():
    # Get all lessons for the current user
    lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.date_modified.desc()).all()
    
    return render_template('lesson_list.html', lessons=lessons)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create-lesson', methods=['GET', 'POST'])
@login_required
def create_lesson_form():
    form = LessonForm()
    if form.validate_on_submit():
        # Create new lesson directly
        lesson = Lesson(
            user_id=current_user.id,
            grade_level=form.grade_level.data,
            topic=form.topic.data,
            teaching_strategy=form.teaching_strategy.data
        )
        
        # Generate lesson plan content
        try:
            lesson_plan = generate_lesson_plan(
                form.grade_level.data,
                form.topic.data,
                form.teaching_strategy.data
            )
            lesson.generated_plan = lesson_plan
        except Exception as e:
            flash(f'Error generating lesson plan: {str(e)}')
            return render_template('create_lesson.html', form=form)
        
        # Save to database
        db.session.add(lesson)
        db.session.commit()
        
        flash('Lesson plan created successfully!')
        return redirect(url_for('edit_lesson_form', lesson_id=lesson.id))
        
    return render_template('create_lesson.html', form=form)

@app.route('/edit-lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson_form(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    form = EditLessonForm()
    
    if request.method == 'GET':
        # Pre-populate the form with existing lesson content
        form.lesson_content.data = lesson.generated_plan
    
    if form.validate_on_submit():
        # Update lesson content
        lesson.generated_plan = form.lesson_content.data
        db.session.commit()
        flash('Lesson plan updated successfully!')
        return redirect(url_for('edit_lesson_form', lesson_id=lesson.id))
    
    return render_template('edit_lesson.html', form=form, lesson=lesson)

@app.route('/textbook-to-lesson', methods=['GET', 'POST'])
@login_required
def textbook_to_lesson():
    form = TextbookContentForm()
    
    if form.validate_on_submit():
        try:
            # Process textbook content
            lesson_plan = process_textbook_content(
                form.grade_level.data,
                form.topic.data,
                form.teaching_strategy.data,
                form.textbook_content.data
            )
            
            # Create new lesson with generated content
            lesson = Lesson(
                user_id=current_user.id,
                grade_level=form.grade_level.data,
                topic=form.topic.data,
                teaching_strategy=form.teaching_strategy.data,
                generated_plan=lesson_plan
            )
            
            # Save to database
            db.session.add(lesson)
            db.session.commit()
            
            flash('تم توليد خطة الدرس من محتوى الكتاب بنجاح!')
            return redirect(url_for('edit_lesson_form', lesson_id=lesson.id))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء معالجة محتوى الكتاب: {str(e)}')
            return render_template('textbook_to_lesson.html', form=form)
    
    return render_template('textbook_to_lesson.html', form=form)
