# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Announcement, Marketplace, Service, Comment
import string, random, os
from captcha.image import ImageCaptcha
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "200 per hour"],
    storage_uri="memory://"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# CAPTCHA configuration
CAPTCHA_LENGTH = 6
CAPTCHA_CHARS = string.ascii_uppercase + string.digits
image_captcha = ImageCaptcha(fonts=['fonts/DejaVuSans.ttf'], width=200, height=60)

def generate_captcha():
    """Generate an 6-character CAPTCHA and image."""
    code = ''.join(random.choice(CAPTCHA_CHARS) for _ in range(CAPTCHA_LENGTH))
    random_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
    image_path = os.path.join('static', 'captchas', f'captcha_{random_name}.png')
    image_captcha.write(code, image_path)
    return code, image_path


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))


# Routes for pages
@app.route('/')
def home():
    # Fetch category counts
    category_counts = {
        'announcements': {
            'Announcements': Announcement.query.filter_by(category='Announcements').count(),
            'General': Announcement.query.filter_by(category='General').count(),
            'MM Service': Announcement.query.filter_by(category='MM Service').count()
        },
        'marketplace': {
            'Buyers': Marketplace.query.filter_by(category='Buyers').count(),
            'Sellers': Marketplace.query.filter_by(category='Sellers').count()
        },
        'services': {
            'Buy': Service.query.filter_by(category='Buy').count(),
            'Sell': Service.query.filter_by(category='Sell').count()
        }
    }
    return render_template('home.html', category_counts=category_counts)

@app.route('/marketplace')
def marketplace():
    # Fetch marketplace category counts
    category_counts = {
        'marketplace': {
            'Buyers': Marketplace.query.filter_by(category='Buyers').count(),
            'Sellers': Marketplace.query.filter_by(category='Sellers').count()
        }
    }
    return render_template('marketplace.html', category_counts=category_counts)

@app.route('/services')
def services():
    # Fetch services category counts
    category_counts = {
        'services': {
            'Buy': Service.query.filter_by(category='Buy').count(),
            'Sell': Service.query.filter_by(category='Sell').count()
        }
    }
    return render_template('services.html', category_counts=category_counts)

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    post_type = request.args.get('type', '')
    posts = []
    if post_type == '' or post_type == 'announcements':
        announcements = Announcement.query.filter(
            (Announcement.title.ilike(f'%{query}%')) |
            (Announcement.content.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'username': post.author.username,
            'date': post.date,
            'post_type': 'announcements'
        } for post in announcements])
    if post_type == '' or post_type == 'marketplace':
        marketplace = Marketplace.query.filter(
            (Marketplace.title.ilike(f'%{query}%')) |
            (Marketplace.description.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.author.username,
            'price': post.price,
            'date': post.date,
            'post_type': 'marketplace'
        } for post in marketplace])
    if post_type == '' or post_type == 'services':
        services = Service.query.filter(
            (Service.title.ilike(f'%{query}%')) |
            (Service.description.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.author.username,
            'price': post.price,
            'date': post.date,
            'post_type': 'services'
        } for post in services])
    return render_template('search.html', posts=posts, query=query, post_type=post_type)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        captcha_code, captcha_image = generate_captcha()
        session['captcha'] = captcha_code
        session['captcha_image'] = captcha_image
        return render_template('login.html', captcha_image=captcha_image)
    
    username = request.form['username']
    password = request.form['password']
    captcha_input = request.form['captcha'].strip().upper()
    
    if captcha_input != session.get('captcha'):
        flash('Invalid CAPTCHA', 'danger')
        captcha_code, captcha_image = generate_captcha()
        session['captcha'] = captcha_code
        session['captcha_image'] = captcha_image
        return render_template('login.html', captcha_image=captcha_image)
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        captcha_image = session.get('captcha_image')
        session.pop('captcha', None)
        session.pop('captcha_image', None)
        if captcha_image:
            try:
                os.remove(captcha_image)
            except OSError as e:
                print(f"Error deleting CAPTCHA image: {e}")
        return redirect(url_for('home'))
    
    flash('Invalid username or password', 'danger')
    captcha_code, captcha_image = generate_captcha()
    session['captcha'] = captcha_code
    session['captcha_image'] = captcha_image
    return render_template('login.html', captcha_image=captcha_image)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, avatar='default.jpg')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/category/<post_type>/<category>')
def category(post_type, category):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    posts = []
    total_pages = 0
    if post_type == 'announcements':
        pagination = Announcement.query.filter_by(category=category).order_by(Announcement.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        posts = [{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'username': post.author.username,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='announcement', post_id=post.id).count()
        } for post in pagination.items]
        total_pages = pagination.pages
    elif post_type == 'marketplace':
        pagination = Marketplace.query.filter_by(category=category).order_by(Marketplace.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        posts = [{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.author.username,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='marketplace', post_id=post.id).count()
        } for post in pagination.items]
        total_pages = pagination.pages
    elif post_type == 'services':
        pagination = Service.query.filter_by(category=category).order_by(Service.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        posts = [{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.author.username,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='service', post_id=post.id).count()
        } for post in pagination.items]
        total_pages = pagination.pages
    else:
        return render_template('404.html'), 404
    return render_template('category.html', post_type=post_type, category=category, page=page, posts=posts, total_pages=total_pages)

@app.route('/post/<post_type>/<int:post_id>')
@limiter.limit("30 per minute")
@login_required
def post_detail(post_type, post_id):
    if post_type not in ['announcements', 'marketplace', 'services']:
        return render_template('404.html'), 404
    post = None
    comments = []
    user = None
    if post_type == 'announcements':
        post = Announcement.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='announcement', post_id=post_id).order_by(Comment.date.desc()).all()
        user = User.query.get_or_404(post.user_id)
    elif post_type == 'marketplace':
        post = Marketplace.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='marketplace', post_id=post_id).order_by(Comment.date.desc()).all()
        user = User.query.get_or_404(post.user_id)
    elif post_type == 'services':
        post = Service.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='service', post_id=post_id).order_by(Comment.date.desc()).all()
        user = User.query.get_or_404(post.user_id)
    post_count = len(user.announcements) + len(user.marketplace_posts) + len(user.services)
    return render_template('post_detail.html', post_type=post_type, post=post, comments=comments, user=user, post_count=post_count)

@app.route('/profile/<username>')
@login_required
def profile_detail(username):
    user = User.query.filter_by(username=username).first_or_404()
    post_count = len(user.announcements) + len(user.marketplace_posts) + len(user.services)
    posts = []
    for post in user.announcements:
        posts.append({
            'post_type': 'announcements',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='announcement', post_id=post.id).count()
        })
    for post in user.marketplace_posts:
        posts.append({
            'post_type': 'marketplace',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='marketplace', post_id=post.id).count()
        })
    for post in user.services:
        posts.append({
            'post_type': 'services',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='service', post_id=post.id).count()
        })
    return render_template('profile_detail.html', user=user, post_count=post_count, posts=posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)