from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Function to call DeepSeek R1 7B Chat API locally
API_URL = "http://localhost:11434/api/generate"

def generate_feedback(summary):
    headers = {"Content-Type": "application/json"}
    
    # Strict prompt to generate crisp feedback (100 words max)
    prompt = f"""
    Evaluate the following summary based on relevance, coherence, grammar, and clarity.
    Provide:
    1. **A concise feedback (within 100 words)**
    2. **A score out of 100**.
    
    Format your response strictly like this:
    ---
    Feedback: <your feedback>
    Score: <a number between 0 to 100>
    ---
    
    Summary: "{summary}"
    """
    
    payload = {
        "model": "deepseek-r1:7b",
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Check if the response is successful
    if response.status_code != 200:
        return "Feedback: Unable to generate feedback.\nScore: 0"
    
    # Extract the AI response
    generated_text = response.json().get("response", "")
    
    # ✅ Step 1: Remove unwanted tags and thoughts
    generated_text = re.sub(r'<.*?>', '', generated_text)  # Removes <think> tags
    
    # ✅ Step 2: Extract feedback
    feedback_match = re.search(r"Feedback:\s*(.*?)\n", generated_text, re.DOTALL)
    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback provided."
    
    # ✅ Step 3: Extract the score
    score_match = re.search(r"Score:\s*(\d+)", generated_text)
    score = int(score_match.group(1)) if score_match else 0
    
    # ✅ Step 4: Return clean feedback and score
    return feedback, score


@app.route('/evaluate_summary', methods=['POST'])
def evaluate_summary():
    data = request.get_json()
    summary = data.get("summary")
    
    # Validate if summary exists
    if not summary:
        return jsonify({
            "score": 0,
            "feedback": "No summary provided. Please provide a valid summary."
        })
    
    # Call DeepSeek to generate feedback
    feedback, score = generate_feedback(summary)
    
    # Build the response object
    evaluation = {
        "score": score,
        "feedback": feedback
    }

    return jsonify(evaluation)


if __name__ == '__main__':
    app.run(debug=True)
