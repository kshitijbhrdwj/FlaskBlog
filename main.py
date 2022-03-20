from datetime import datetime
from flask import Flask,render_template, request, url_for, flash, redirect, abort
from forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from flask_bcrypt import Bcrypt
import os

app =Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category = 'info'
app.config['SECRET_KEY'] = '5791628bb0b13ce0ce0c676dfde280ba245'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskblog'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model,UserMixin):

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False, )
    posts = db.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"

class Posts(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(12), nullable=True, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}','{self.date_posted}')"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def home():
    #posts = Posts.query.all()
    page = request.args.get('page',1, type='int')
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(per_page=3, page=page)
    return render_template('home.html',posts=posts,title='Home')

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if request.method == 'POST':

            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            if User.query.filter_by(username=username).first():
                flash (f'The username - "{username}" is already taken','danger')
                return redirect(url_for('register'))


            if User.query.filter_by(email=email).first():
               flash (f'The Email - "{email}" is already taken', 'danger')
               return redirect(url_for('register'))

            entry = User(username=username,email=email,password=hashed_password)

            db.session.add(entry)
            db.session.commit()

        flash(f'Account Created for {form.username.data}.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'You have been logged in.', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
                flash(f'Login Unsuccessful!.', 'danger')
    return render_template('login.html',title='Login',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    _,f_ext = form_picture.data.filename.split('.')
    prefix = str(current_user.username)
    picture_fn = prefix+'.'+f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.data.save(picture_path)
    
    return picture_fn


@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture)
            current_user.image_file = picture_file

        if User.query.filter_by(username = form.username).first():
                flash (f'The username - "{form.username}" is already taken','danger')
                return redirect(url_for('register'))


        if User.query.filter_by(email=form.email).first():
                flash (f'The Email - "{form.email}" is already taken', 'danger')
                return redirect(url_for('register'))
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash (f'Account details have been updated', 'success')
        return redirect(url_for('account'))

    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title = form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Posts.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Posts.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Posts.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)


