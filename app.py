import os
import re
import uuid
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    videos = db.relationship('Video', backref='owner', lazy=True)
    resources = db.relationship('Resource', backref='owner', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    video_id = db.Column(db.String(50))
    playlist = db.Column(db.String(100), default="General")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    type = db.Column(db.String(20)) 
    content = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# --- Helper Functions ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def extract_yt_id(url):
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    return match.group(1) if match else None

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Handle Video Add
    if request.method == 'POST' and 'youtube_url' in request.form:
        url = request.form.get('youtube_url')
        playlist = request.form.get('playlist', 'General')
        vid_id = extract_yt_id(url)
        if vid_id:
            new_vid = Video(title=request.form.get('title'), video_id=vid_id, playlist=playlist, owner=current_user)
            db.session.add(new_vid)
            db.session.commit()
            return redirect(url_for('dashboard'))

    # Handle Link Add
    if request.method == 'POST' and 'link_url' in request.form:
        new_link = Resource(title=request.form.get('title'), type='link', 
                           content=request.form.get('link_url'), owner=current_user)
        db.session.add(new_link)
        db.session.commit()
        return redirect(url_for('dashboard'))

    # Handle PDF Upload
    if request.method == 'POST' and 'pdf_file' in request.files:
        file = request.files['pdf_file']
        if file and file.filename.endswith('.pdf'):
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            new_pdf = Resource(title=request.form.get('title'), type='pdf', 
                              content=unique_filename, owner=current_user)
            db.session.add(new_pdf)
            db.session.commit()
            return redirect(url_for('dashboard'))

    # --- CHANGED LOGIC FOR DASHBOARD ---
    videos = Video.query.filter_by(user_id=current_user.id).all()
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    
    # Calculate Playlists and Video Counts
    # Format: {'Math': 5, 'Physics': 2}
    playlists = {}
    for vid in videos:
        if vid.playlist not in playlists:
            playlists[vid.playlist] = 0
        playlists[vid.playlist] += 1

    return render_template('dashboard.html', playlists=playlists, resources=resources)

# --- NEW ROUTE FOR VIEWING VIDEOS ---
@app.route('/playlist/<name>')
@login_required
def view_playlist(name):
    # Fetch only videos for this specific playlist
    videos = Video.query.filter_by(user_id=current_user.id, playlist=name).all()
    if not videos:
        flash("Playlist not found or empty.")
        return redirect(url_for('dashboard'))
    
    return render_template('playlist.html', playlist_name=name, videos=videos)

# --- EDIT & DELETE ROUTES ---

@app.route('/video/delete/<int:id>')
@login_required
def delete_video(id):
    video = Video.query.get_or_404(id)
    if video.owner != current_user:
        abort(403)
    
    # Save the playlist name before deleting so we can redirect back to it
    playlist_name = video.playlist
    db.session.delete(video)
    db.session.commit()
    
    # Check if any videos remain in this playlist
    remaining = Video.query.filter_by(user_id=current_user.id, playlist=playlist_name).first()
    if remaining:
        return redirect(url_for('view_playlist', name=playlist_name))
    else:
        return redirect(url_for('dashboard'))

@app.route('/video/edit/<int:id>', methods=['POST'])
@login_required
def edit_video(id):
    video = Video.query.get_or_404(id)
    if video.owner != current_user:
        abort(403)
        
    old_playlist = video.playlist
    video.title = request.form.get('title')
    video.playlist = request.form.get('playlist')
    db.session.commit()
    
    # If playlist changed or stayed same, deciding where to go is tricky.
    # Simple logic: Go to the new playlist view.
    return redirect(url_for('view_playlist', name=video.playlist))

@app.route('/resource/delete/<int:id>')
@login_required
def delete_resource(id):
    resource = Resource.query.get_or_404(id)
    if resource.owner != current_user:
        abort(403)
    if resource.type == 'pdf':
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], resource.content))
        except:
            pass
    db.session.delete(resource)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/resource/edit/<int:id>', methods=['POST'])
@login_required
def edit_resource(id):
    resource = Resource.query.get_or_404(id)
    if resource.owner != current_user:
        abort(403)
    resource.title = request.form.get('title')
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)