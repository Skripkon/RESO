from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route('/')
def main_page():
    page = render_template("main_page.html")
    return page


@app.route('/execute_function', methods=['POST'])
def execute_function():
    # Your Python function logic goes here
    rand_number = random.random()
    result = f"Random number: {round(rand_number, 5)}"
    return jsonify(result=result)

if __name__ == "__main__":
    app.run(debug=True)
