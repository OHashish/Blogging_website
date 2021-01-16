from flask import render_template, flash,redirect , url_for , request ,session,jsonify
from app import app, db, admin,bcrypt
from .forms import LoginForm , RegisterForm,PostForm,BlogForm,ResetPasswordForm
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from .models import Posts ,User,Blog,follow_table
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_uploads  import UploadSet,configure_uploads,IMAGES
import logging
import flask_whooshalchemy as wa
enable_search=True
WHOOSH_BASE='whoosh'  
wa.whoosh_index(app,Blog)

logger_I=logging.getLogger(__name__)


logger_I.setLevel(logging.DEBUG)


formatter= logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'
)
file_handler=logging.FileHandler('beans.log')

file_handler.setFormatter(formatter)

logger_I.addHandler(file_handler)





bootstrap = Bootstrap(app)


admin.add_view(ModelView(Posts,db.session))
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Blog,db.session))


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'flask_project/app/static'
configure_uploads(app, photos)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/post_blog', methods=['GET', 'POST'])
@login_required
def post_blog():
	filename=None
	form= PostForm()
	title = form.title.data
	body = form.body.data
	blogs = Blog.query.filter_by(user=current_user)
	selected_blog=request.form.get("selected_blog")
	if form.validate_on_submit():
		photo = request.files['photo']
		if photo.filename!='':
			filename = photos.save(request.files['photo'])
		if selected_blog =="":
			flash('No blog was selected.',"danger")
		else:
			get_blog=Blog.query.filter_by(id=selected_blog).one()
			p = Posts(date=datetime.now(),title=form.title.data,body=form.body.data,image_name=filename,blog=get_blog,author=current_user.username)
			logger_I.info(current_user.username + " posted to blog named " +get_blog.blog_name)
			db.session.add(p)
			db.session.commit()
			return redirect(url_for('post_blog'))
		logger_I.debug(current_user.username + " failed to post to blog")
	return render_template('post.html',form=form,blogs=blogs)


@app.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
	form= BlogForm()
	name = form.blog_name.data
	if request.method == 'POST':
		if not name:
			flash('Blog name is required',"danger")
		else:
			p = Blog(blog_name=name,user=current_user)
			db.session.add(p)
			db.session.commit()
			logger_I.info(current_user.username + " created a new blog")
			return redirect(url_for('post_blog'))
		logger_I.debug(current_user.username + " failed to create a new blog")
	return render_template('create_blog.html', form=form)



@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Posts.query.filter_by(id=post_id).one()
    return render_template('post_page.html', post=post)

@app.route('/delete_post', methods=['GET', 'POST'])
@login_required
def delete_post():
	data=request.form['id']
	Posts.query.filter_by(id=data).delete()
	db.session.commit()
	logger_I.info(current_user.username + " deleted a post.")
	return jsonify()

@app.route("/posted/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update(post_id):
	form = PostForm()
	post = Posts.query.get_or_404(post_id)
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		logger_I.info(current_user.username + " updated a post.")
		return redirect(url_for('posted'))
	elif request.method == 'GET':
		form.title.data = post.title
		form.body.data = post.body
	return render_template('update.html', title='Update Post',form=form)

@app.route('/posted', methods=['GET', 'POST'])
@login_required
def posted():
	pos=Posts.query.order_by(Posts.date.desc()).join(Blog).filter(Blog.user_id == current_user.id).all()
	return render_template('posted.html', title='Posted', p = pos)

@app.route('/search', methods=['GET', 'POST'])
@login_required		
def search():
	blogs=Blog.query.whoosh_search(request.args.get('query')).all()
	print(blogs)
	return render_template('view_blogs.html', blogs = blogs)



@app.route('/follow', methods=['GET', 'POST'])
@login_required
def follow():
	flag=0
	data=request.form['id']
	clicked_blog=Blog.query.filter_by(blog_name=data).first()
	blogs=current_user.followed_blogs
	for blog in blogs:
		if blog==clicked_blog:
			logger_I.info(current_user.username + " unfollowed a blog")
			clicked_blog.user_followers.remove(current_user)
			flag=1
			break

	if flag==0:
		logger_I.info(current_user.username + " followed a blog")
		clicked_blog.user_followers.append(current_user)
	db.session.commit()

	return jsonify()

@app.route('/general', methods=['GET', 'POST'])
@login_required
def general():
	posts=Posts.query.order_by(Posts.date.desc()).join(Blog).filter(Blog.user_id != current_user.id).all()
	return render_template('general.html', title='General', posts = posts)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
	f_blog=current_user.followed_blogs
	blogs = Blog.query.filter(Blog.user_followers.any(id=current_user.id)).all()
	li=[]
	for i in blogs:
		l=i.posts
		for pp in l:
			li.append(pp)

	da=sorted(li,key=lambda post: post.date,reverse=True)
	return render_template('home.html', title='home', p= da)

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()

	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			if bcrypt.check_password_hash(user.password,form.password.data):
				login_user(user,remember=form.remember.data)
				logger_I.info(user.username+" just logged in")
				return redirect(url_for('home'))
			logger_I.warning(user.username+" failed to login.")
		flash('Incorrect username or password. Please try again.','danger')
		logger_I.warning("An attemp to login has failed .")
		return redirect(url_for('login'))


	return render_template('login.html',form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
	form=RegisterForm()
	flag=0
	if form.validate_on_submit():
		hash_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User.query.filter_by(username=form.username.data).first()
		email=User.query.filter_by(email=form.email.data).first()
		if user:
			flash('Username already in use',"danger")
			flag=1
		if email:
			flash('Email already in use',"danger")
			flag=1
		if flag==0:
			new_user=User(username=form.username.data,email=form.email.data,password=hash_pass)
			db.session.add(new_user)
			db.session.commit()
			logger_I.info("An account has been created with username: "+new_user.username)
			flash("Your account has been created! You can now login","success")
			return redirect(url_for('login'))
	logger_I.warning("A failed registeration attempt has occured.")
	return render_template('signup.html',form=form)

@app.route('/reset_password',methods=['GET','POST'])
@login_required
def reset_password():
	form=ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User.query.filter_by(username=current_user.username).first()
		user.password=hashed_password
		db.session.commit()
		flash('Your password has been reset', 'success')
		logger_I.info(user.username+" has changed password.")
		return redirect(url_for('home'))
	return render_template('reset_password.html',form=form)

@app.route('/account')
@login_required
def account():
	return render_template('account.html',title="Account")

@app.route('/logout')
@login_required
def logout():
	logger_I.info(current_user.username+" logged out.")
	logout_user()
	return redirect(url_for("login"))

if __name__=='__main__':
	app.run(debug=True)