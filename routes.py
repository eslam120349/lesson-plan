import os
import tempfile
from flask import render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Lesson, Presentation
from forms import LoginForm, RegistrationForm, LessonForm, EditLessonForm, ARLessonForm, UserProfileForm, WhatsAppMessageForm
from lesson_generator import generate_lesson_plan,gpt_plans
from ppt_generator import create_presentation
from textbook_processor import process_textbook_content
from whatsapp_sender import process_excel_file, open_whatsapp_web
from urllib.parse import urlparse

@app.route('/')
def index():
    # Get the language from session, default to English
    language = session.get('language', 'en')
    return render_template('index_new.html', language=language)

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
        teaching_strategy=data.get('teaching_strategy'),
        language=data.get('language')
    )

    # Generate lesson plan content
    try:
        lesson_plan = generate_lesson_plan(
            data.get('grade_level'),
            data.get('topic'),
            data.get('teaching_strategy')
            ,data.get('language')
        )
        lesson.generated_plan = lesson_plan
        lesson.gpt_plan=gpt_plans(data.get('grade_level'),data.get('topic'),data.get('teaching_strategy'),data.get('language'))


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

    # Get the language from session, default to English
    language = session.get('language', 'en')

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

    return render_template('login.html', form=form, language=language)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Get the language from session, default to English
    language = session.get('language', 'en')

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, language=language)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's lessons
    total_lessons = Lesson.query.filter_by(user_id=current_user.id).count()
    recent_lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.date_modified.desc()).limit(5).all()

    # Get the language from session, default to English
    language = session.get('language', 'en')

    return render_template('dashboard.html',
                          total_lessons=total_lessons,
                          recent_lessons=recent_lessons,
                          language=language)

@app.route('/lessons')
@login_required
def get_lessons_page():
    # Get all lessons for the current user
    lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.date_modified.desc()).all()

    # Get the language from session, default to English
    language = session.get('language', 'en')

    return render_template('lesson_list.html', lessons=lessons, language=language)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/set-language/<language>')
def set_language(language):
    # Store the selected language in session
    session['language'] = language
    # Redirect back to the previous page
    return redirect(request.referrer or url_for('index'))

@app.route('/create-lesson', methods=['GET', 'POST'])
@login_required
def create_lesson_form():
    # Get the language from session, default to English
    language = session.get('language', 'en')

    form = LessonForm()
    if form.validate_on_submit():
        # Create new lesson directly
        lesson = Lesson(
            user_id=current_user.id,
            grade_level=form.grade_level.data,
            topic=form.topic.data,
            teaching_strategy=form.teaching_strategy.data,
            language=form.language.data
        )

        # Generate lesson plan content
        try:
            lesson_plan = generate_lesson_plan(
                form.grade_level.data,
                form.topic.data,
                form.teaching_strategy.data
                ,form.language.data
            )
            lesson.generated_plan = lesson_plan
            lesson.gpt_plan=gpt_plans(form.grade_level.data,form.topic.data,form.teaching_strategy.data,form.language.data )
        except Exception as e:
            flash(f'Error generating lesson plan: {str(e)}')
            return render_template('create_lesson.html', form=form, language=language)

        # Save to database
        db.session.add(lesson)
        db.session.commit()

        flash('Lesson plan created successfully!')
        return redirect(url_for('edit_lesson_form', lesson_id=lesson.id))

    return render_template('create_lesson.html', form=form, language=language)

@app.route('/edit-lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson_form(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('index'))

    # Get the language from session, default to English
    language = session.get('language', 'en')

    form = EditLessonForm()

    if request.method == 'GET':
        form.generated_plan.data = lesson.generated_plan
        form.gpt_plan.data = lesson.gpt_plan

    if form.validate_on_submit():
        lesson.generated_plan = form.generated_plan.data
        lesson.gpt_plan = form.gpt_plan.data
        db.session.commit()
        flash('Lesson plan updated successfully!')
        return redirect(url_for('edit_lesson_form', lesson_id=lesson.id))

    return render_template('edit_lesson.html', form=form, lesson=lesson, language=language)

@app.route('/textbook-to-lesson', methods=['GET', 'POST'])
@login_required
def textbook_to_lesson():
    # Get the language from session, default to English
    language = session.get('language', 'en')

    form = ARLessonForm()

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
            return render_template('textbook_to_lesson.html', form=form, language=language)

    return render_template('textbook_to_lesson.html', form=form, language=language)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    language = session.get('language', 'en')
    form = UserProfileForm()

    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect' if language == 'en' else 'كلمة المرور الحالية غير صحيحة')
            return render_template('user.html', form=form, language=language)

        # Update user information
        current_user.name = form.name.data
        current_user.email = form.email.data

        # Update password if new password is provided
        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash('Profile updated successfully!' if language == 'en' else 'تم تحديث الملف الشخصي بنجاح!')
        return redirect(url_for('user'))

    # Pre-fill form with current user data
    form.name.data = current_user.name
    form.email.data = current_user.email

    return render_template('user.html', form=form, language=language)

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    language = session.get('language', 'en')

    # Delete user's lessons first (due to foreign key constraint)
    Lesson.query.filter_by(user_id=current_user.id).delete()

    # Delete user
    db.session.delete(current_user)
    db.session.commit()

    flash('Your account has been deleted.' if language == 'en' else 'تم حذف حسابك.')
    return redirect(url_for('index'))

@app.route('/whatsapp-sender', methods=['GET', 'POST'])
@login_required
def whatsapp_sender():
    language = session.get('language', 'en')
    form = WhatsAppMessageForm()

    if form.validate_on_submit():
        try:
            # Process the Excel file
            messages = process_excel_file(
                form.excel_file.data,
                form.student_name_column.data,
                form.grades_column.data,
                form.phone_column.data,
                form.message_template.data
            )

            if not messages:
                flash('No valid data found in the Excel file.' if language == 'en' else 'لم يتم العثور على بيانات صالحة في ملف Excel.', 'warning')
                return render_template('whatsapp_sender.html', form=form, language=language)

            # Store messages in session for the results page
            session['whatsapp_messages'] = messages

            # Open WhatsApp Web for the first message
            if messages:
                open_whatsapp_web(messages[0]['phone'], messages[0]['message'])

            # Flash success message
            flash(f'Successfully processed {len(messages)} messages. WhatsApp Web has been opened for the first message.' if language == 'en' else
                  f'تمت معالجة {len(messages)} رسالة بنجاح. تم فتح واتساب ويب للرسالة الأولى.', 'success')

            # Redirect to the same page to avoid form resubmission
            return redirect(url_for('whatsapp_sender'))

        except Exception as e:
            flash(f'Error: {str(e)}' if language == 'en' else f'خطأ: {str(e)}', 'danger')

    return render_template('whatsapp_sender.html', form=form, language=language)

@app.route('/send-whatsapp/<int:index>', methods=['GET'])
@login_required
def send_individual_whatsapp(index):
    messages = session.get('whatsapp_messages', [])

    if not messages or index >= len(messages):
        flash('Invalid message index or no messages available.', 'danger')
        return redirect(url_for('whatsapp_sender'))

    # Open WhatsApp Web for the selected message
    message = messages[index]
    open_whatsapp_web(message['phone'], message['message'])

    flash(f'WhatsApp Web opened for {message["student_name"]}.', 'success')
    return redirect(url_for('whatsapp_sender'))

@app.route('/clear-whatsapp-messages', methods=['POST'])
@login_required
def clear_whatsapp_messages():
    # Clear the WhatsApp messages from the session
    if 'whatsapp_messages' in session:
        session.pop('whatsapp_messages')

    return jsonify({'success': True})
