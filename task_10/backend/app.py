from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='user', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # undergrad/graduate
    duration = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    tuition = db.Column(db.Float)
    deadline = db.Column(db.String(50))

# Create database tables
with app.app_context():
    db.create_all()

# Sample data initialization
def init_db():
    with app.app_context():
        # Add sample programs if none exist
        if not Program.query.first():
            programs = [
                Program(
                    name="Computer Science",
                    level="undergrad",
                    duration="4 years",
                    requirements="High school diploma, Math and Science background",
                    tuition=15000.0,
                    deadline="January 15"
                ),
                Program(
                    name="Business Administration",
                    level="graduate",
                    duration="2 years",
                    requirements="Bachelor's degree, GMAT/GRE scores",
                    tuition=25000.0,
                    deadline="March 1"
                ),
                Program(
                    name="Data Science",
                    level="graduate",
                    duration="1.5 years",
                    requirements="Bachelor's degree in related field, Programming knowledge",
                    tuition=28000.0,
                    deadline="February 15"
                )
            ]
            db.session.add_all(programs)
            db.session.commit()

# Initialize sample data
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple response logic (can be enhanced with NLP later)
    response = process_message(message)
    
    # In a real app, you would save the message and response to the database here
    # user = User.query.filter_by(username='guest').first()
    # if not user:
    #     user = User(username='guest', email='guest@example.com')
    #     db.session.add(user)
    #     db.session.commit()
    # 
    # chat_message = ChatMessage(
    #     user_id=user.id,
    #     message=message,
    #     response=response
    # )
    # db.session.add(chat_message)
    # db.session.commit()
    
    return jsonify({'response': response})

def process_message(message):
    # Simple keyword-based response system
    if any(word in message for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I assist you with your university admission questions today?"
    
    elif 'program' in message or 'course' in message:
        programs = Program.query.all()
        if not programs:
            return "We offer various programs at both undergraduate and graduate levels. Could you specify which level you're interested in?"
        
        response = "Here are some of our programs:\n"
        for program in programs:
            response += f"- {program.name} ({program.level}): ${program.tuition}/year\n"
        return response
    
    elif 'requirement' in message or 'need' in message or 'document' in message:
        if 'undergrad' in message:
            return "For undergraduate programs, you'll need: High school diploma, SAT/ACT scores, letters of recommendation, and a personal statement."
        elif 'grad' in message or 'master' in message:
            return "For graduate programs, you'll need: Bachelor's degree, GRE/GMAT scores, letters of recommendation, statement of purpose, and resume/CV."
        else:
            return "Admission requirements vary by program level. Are you interested in undergraduate or graduate programs?"
    
    elif 'deadline' in message or 'when' in message and 'apply' in message:
        if 'fall' in message:
            return "The application deadline for Fall admission is typically January 15th."
        elif 'spring' in message:
            return "The application deadline for Spring admission is typically October 1st."
        else:
            return "Application deadlines vary by program. The general deadlines are January 15th for Fall and October 1st for Spring."
    
    elif 'tuition' in message or 'cost' in message or 'fee' in message:
        programs = Program.query.all()
        if not programs:
            return "Tuition varies by program. Could you specify which program you're interested in?"
        
        response = "Here are the tuition fees for our programs:\n"
        for program in programs:
            response += f"- {program.name}: ${program.tuition}/year\n"
        return response
    
    elif 'contact' in message or 'email' in message or 'phone' in message:
        return "You can contact our admissions office at:\n\nEmail: admissions@university.edu\nPhone: (123) 456-7890\nAddress: 123 University Ave, City, State 12345"
    
    else:
        return "I'm not sure I understand. Could you please rephrase your question? You can ask about programs, admission requirements, deadlines, or tuition fees."

# API Endpoints for Programs
@app.route('/api/programs', methods=['GET'])
def get_programs():
    programs = Program.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'level': p.level,
        'duration': p.duration,
        'requirements': p.requirements,
        'tuition': p.tuition,
        'deadline': p.deadline
    } for p in programs])

@app.route('/api/programs/<int:id>', methods=['GET'])
def get_program(id):
    program = Program.query.get_or_404(id)
    return jsonify({
        'id': program.id,
        'name': program.name,
        'level': program.level,
        'duration': program.duration,
        'requirements': program.requirements,
        'tuition': program.tuition,
        'deadline': program.deadline
    })

if __name__ == '__main__':
    app.run(debug=True)
