from flask import Flask, render_template, jsonify, request, send_file
import random
from utils.midi2mp3 import midi2mp3

app = Flask(__name__)

@app.route('/')
def main_page():
    page = render_template("main_page.html")
    return page

@app.route('/convert_page')
def convert_page():
    return render_template("convert_page.html")

@app.route('/execute_function', methods=['POST'])
def execute_function():
    # Your Python function logic goes here
    rand_number = random.random()
    result = f"Random number: {round(rand_number, 5)}"
    return jsonify(result=result)

@app.route('/convert_midi2mp3', methods=['POST'])
def convert_midi2mp3():
    if request.method == 'POST':
        midi_file = request.files['midi_file']
        midi_file.save('uploaded_midi.mid')
        mp3_file_path = midi2mp3('uploaded_midi.mid')
        return send_file(mp3_file_path, as_attachment=True)
    else:
        return 'Method not supported!'

if __name__ == "__main__":
    app.run(debug=True)
