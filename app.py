from flask import Flask,render_template
from auth.routes import auth_bp
from functionality.routes import func_bp

app = Flask(__name__, template_folder='templates')

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(func_bp, url_prefix='/func')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
