from flask import Flask, render_template, request, jsonify
from models.llm_model import OllamaModel
from multiagent.ngl_aggregator import NGLAggregator
import json

app = Flask(__name__)
model = OllamaModel()
aggregator = NGLAggregator()

# Store responses for aggregation
responses = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_experts():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "Missing question"}), 400

    expert_types = ["surgeon", "physiotherapist", "doctor"]
    current_responses = {}

    try:
        # Get responses from all experts
        for expert_type in expert_types:
            response = model.get_expert_response(question, expert_type)
            current_responses[expert_type] = response

        # Store responses for aggregation
        responses[question] = current_responses

        return jsonify({
            "status": "success",
            "responses": current_responses
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/aggregate', methods=['POST'])
def aggregate_responses():
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Missing question"}), 400
    
    if question not in responses:
        return jsonify({"error": "No responses found for this question"}), 404

    try:
        # Get the responses for this question
        current_responses = responses[question]
        
        # Use the NGL aggregator to analyze responses
        aggregated_analysis = aggregator.aggregate_responses(current_responses)
        
        return jsonify(aggregated_analysis)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False) 