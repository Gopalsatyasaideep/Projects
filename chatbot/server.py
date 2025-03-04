from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__, static_folder="static", template_folder="templates")

api_key = "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"

def get_chatgpt_response(prompt):
    client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@app.route("/")
def home():
    return render_template("index.html")  # Make sure index.html is inside a 'templates' folder

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    response = get_chatgpt_response(user_prompt)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
