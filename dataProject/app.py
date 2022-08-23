from flask import Flask, render_template

app = Flask(__name__)


#Using the below, the popup message appears on the page load of index.html
#0x00001000 - This makes the popup appear over the browser window
@app.route('/')
def index():
    return render_template('main.html')

#Using the below, the popup message appears when the button is clicked on the webpage.
#0x00001000 - This makes the popup appear over the browser window
@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test_user_data')
def test2():
    return render_template('test2.html')

if __name__ == "__main__":
    app.run(debug=True)