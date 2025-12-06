from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
import torch
import random

app = Flask(__name__)

# Load transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Course database
courses = {
    "Python for Beginners": "Learn the basics of Python programming including variables, loops, and functions.",
    "Machine Learning A-Z": "Master machine learning algorithms, data preprocessing, and model evaluation techniques.",
    "Web Development Bootcamp": "Become a full-stack web developer using HTML, CSS, JavaScript, and backend frameworks.",
    "Advanced Data Science": "Deep dive into big data analysis, NLP, deep learning, and statistical modeling.",
    "Intro to Artificial Intelligence": "Understand the fundamentals of AI including neural networks and search algorithms.",
    "Java Programming Essentials": "Start building desktop and Android applications using Java.",
    "Data Visualization with Tableau": "Create interactive and insightful visualizations with Tableau and dashboards.",
    "SQL for Data Analysis": "Learn SQL to manipulate, query, and analyze large datasets efficiently.",
    "Frontend Mastery with React": "Master modern UI development using React, Redux, and component-based architecture.",
    "Backend Development with Node.js": "Build scalable APIs using Node.js, Express, and MongoDB."
}

# Precompute embeddings for all course descriptions
course_titles = list(courses.keys())
course_descriptions = list(courses.values())
course_embeddings = model.encode(course_descriptions, convert_to_tensor=True)

def recommend_courses(user_input):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    
    # Compute cosine similarities
    similarities = util.cos_sim(user_embedding, course_embeddings)[0]
    
    # Get top 3 matches
    top_indices = torch.topk(similarities, k=3).indices.tolist()
    recommended = []
    for idx in top_indices:
        title = course_titles[idx]
        recommended.append({"title": title, "description": courses[title]})
    
    return recommended

@app.route('/')
def home():
    return render_template('index.html', courses=courses)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input', '').strip()
    if not user_input:
        return jsonify({"error": "Please enter your interest"})
    
    recommendations = recommend_courses(user_input)
    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    app.run(debug=True)
