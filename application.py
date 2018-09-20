from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY 

login_manager = LoginManager()
login_manager.init_app(app)

# Mock DB
users = {'foo@bar.tld': {'password': generate_password_hash('secret')}}

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    user.is_authenticated = check_password_hash(request.form['password'], users[email]['password'])

@app.route('/')
def index():
    return str(users['foo@bar.tld']['password'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = request.form['email']

    try:
        if check_password_hash(users[email]['password'], request.form['password']):
            user = User()
            user.id = email
            login_user(user)
            return redirect(url_for('protected'))
    
    except KeyError:
        return 'Incorrect username or password'

    return 'Bad login'

@app.route('/protected')
@login_required
def protected():
    return f'Logged in as: {current_user.id}'

@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'