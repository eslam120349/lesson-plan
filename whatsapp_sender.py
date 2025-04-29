import pandas as pd
import urllib.parse
import webbrowser
import os
import tempfile
from werkzeug.utils import secure_filename

def process_excel_file(file, student_name_column, grades_column, phone_column, message_template):
    """
    Process the uploaded Excel file and prepare WhatsApp messages.
    
    Args:
        file: The uploaded file object
        student_name_column: Column number for student names (1-based)
        grades_column: Column number for grades (1-based)
        phone_column: Column number for phone numbers (1-based)
        message_template: Template string for the message
        
    Returns:
        A list of dictionaries containing student data and formatted messages
    """
    # Save the uploaded file to a temporary location
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(file.filename)
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)
    
    try:
        # Convert column numbers to 0-based indices for pandas
        student_name_col_idx = student_name_column - 1
        grades_col_idx = grades_column - 1
        phone_col_idx = phone_column - 1
        
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Prepare the messages
        messages = []
        
        for _, row in df.iterrows():
            try:
                student_name = str(row.iloc[student_name_col_idx])
                grade = str(row.iloc[grades_col_idx])
                phone = str(row.iloc[phone_col_idx])
                
                # Format the phone number (ensure it starts with country code)
                if not phone.startswith('+'):
                    # Assuming default country code is +1, adjust as needed
                    if phone.startswith('0'):
                        phone = '+2' + phone[1:]  # For Egypt
                    else:
                        phone = '+' + phone
                
                # Remove any spaces or special characters from the phone number
                phone = ''.join(c for c in phone if c.isdigit() or c == '+')
                
                # Format the message
                message = message_template.format(student_name=student_name, grade=grade)
                
                messages.append({
                    'student_name': student_name,
                    'grade': grade,
                    'phone': phone,
                    'message': message
                })
            except Exception as e:
                # Skip rows with errors
                continue
        
        return messages
    
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

def open_whatsapp_web(phone, message):
    """
    Open WhatsApp Web with a pre-composed message.
    
    Args:
        phone: The recipient's phone number (with country code)
        message: The message to send
        
    Returns:
        None
    """
    # Encode the message for URL
    encoded_message = urllib.parse.quote(message)
    
    # Create the WhatsApp Web URL
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
    
    # Open the URL in the default browser
    webbrowser.open(url)
