from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

def find_s_algorithm(data):
    hypothesis = ['0'] * (len(data.columns) - 1)  # Assuming last column is the label
    for _, row in data.iterrows():
        if row[-1].strip().lower() == 'yes':  # Adjust based on the dataset's positive class label
            for i in range(len(hypothesis)):
                if hypothesis[i] == '0':
                    hypothesis[i] = row[i]
                elif hypothesis[i] != row[i]:
                    hypothesis[i] = '?'
    return hypothesis

def candidate_elimination_algorithm(data):
    S = ['0'] * (len(data.columns) - 1)  # Specific boundary
    G = [['?' for _ in range(len(S))]]   # General boundary

    for _, row in data.iterrows():
        if row[-1].strip().lower() == 'yes':  # Positive example
            for i in range(len(S)):
                if S[i] == '0':
                    S[i] = row[i]
                elif S[i] != row[i]:
                    S[i] = '?'
            G = [g for g in G if all(g[i] == '?' or g[i] == S[i] for i in range(len(S)))]
        else:  # Negative example
            new_G = []
            for g in G:
                if any(g[i] == '?' or g[i] == row[i] for i in range(len(g))):
                    for i in range(len(g)):
                        if g[i] == '?':
                            new_hypothesis = g[:]
                            new_hypothesis[i] = S[i] if S[i] != '0' else row[i]
                            new_G.append(new_hypothesis)
            G = [g for g in new_G if not any(g[i] != '?' and g[i] == row[i] for i in range(len(g)))]

    G = [g for g in G if not all(x == '?' for x in g)]
    
    return {"S": S, "G": G}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_dataset():
    if 'dataset' not in request.files or not request.files['dataset'].filename:
        return "No file uploaded. Please upload a CSV file.", 400
    
    file = request.files['dataset']
    algorithm = request.form.get('algorithm')
    
    try:
        data = pd.read_csv(file)
    except Exception as e:
        return f"Error reading the CSV file: {e}", 400

    if algorithm == 'find_s':
        result = find_s_algorithm(data)
        result_text = f"Find-S Algorithm Result: {result}"
    elif algorithm == 'candidate_elimination':
        result = candidate_elimination_algorithm(data)
        result_text = f"Candidate Elimination Algorithm Result: {result}"
    else:
        result_text = "Invalid algorithm selected."

    return result_text

if __name__ == '__main__':
    app.run(debug=True)
