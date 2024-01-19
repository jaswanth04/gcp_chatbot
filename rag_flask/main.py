from flask import Flask, render_template, request

from rag.rag import Chatter
chatter = Chatter()


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        query = request.form['userInput']
        reply = chatter.get_response(query)

        # Render the template with the API response
        data = {'response': reply}
        print(f'Message to pass to front end : {data}')
        return data
