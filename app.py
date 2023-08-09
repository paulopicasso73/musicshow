from flask import Flask, render_template, request, redirect
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'



shows = [
    {'name': 'Rock Concert', 'tickets': 10},
    {'name': 'Jazz Night', 'tickets': 5},
    {'name': 'Pop Festival', 'tickets': 20},
]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    users = {
        "user1": ("password1", "User One"),
        "user2": ("password2", "User Two")
    }

    def __init__(self, username, password, name):
        self.id = username
        self.password = password
        self.name = name

    @classmethod
    def get(cls, username):
        if username in cls.users:
            return cls(username, *cls.users[username])

    @classmethod
    def create(cls, username, password, name):
        cls.users[username] = (password, name)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect('/')
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']

        # Check if the username already exists
        if User.get(username):
            return 'Username already exists', 400

        # Check if the password and confirmation match
        if password != confirm_password:
            return 'Passwords do not match', 400

        # Create the user
        User.create(username, password, name)

        # Redirect to the login page
        return redirect('/login')

    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect('/')
    return render_template('logout.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', shows=shows)

@app.route('/book/<show_name>', methods=['POST'])
@login_required
def book(show_name):
    for show in shows:
        if show['name'] == show_name and show['tickets'] > 0:
            show['tickets'] -= 1
            return render_template('success.html', show_name=show_name)
    return 'Tickets are sold out!', 400


if __name__ == '__main__':
    app.run(debug=True)
