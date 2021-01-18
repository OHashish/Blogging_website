from flask import render_template, flash,redirect , url_for , request ,session,jsonify,abort
from app import app, db, admin,bcrypt
from .forms import LoginForm , RegisterForm,PostForm,BlogForm,ResetPasswordForm
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from .models import Posts ,User,Blog,follow_table,likers
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_uploads  import UploadSet,configure_uploads,IMAGES
import logging
import flask_whooshalchemy as wa
enable_search=True
WHOOSH_BASE='whoosh'
wa.whoosh_index(app,Blog)

logger=logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)


formatter= logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'
)
file_handler=logging.FileHandler('web_app.log')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

bootstrap = Bootstrap(app)


admin.add_view(ModelView(Posts,db.session))
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Blog,db.session))


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'app/static'
configure_uploads(app, photos)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



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
			try:
				filename = photos.save(request.files['photo'])
			except:
				flash('Wrong image format entered .Please try again.',"danger")
				logger.error("Incorrect Image format")
				return redirect(url_for('post_blog'))
			
		if selected_blog =="":
			flash('No blog was selected.',"danger")
		else:
			get_blog=Blog.query.filter_by(id=selected_blog).one()
			p = Posts(date=datetime.now(),title=form.title.data,body=form.body.data,image_name=filename,blog=get_blog,author=current_user.username)
			logger.info(current_user.username + " posted to blog named " +get_blog.blog_name)
			db.session.add(p)
			db.session.commit()
			flash('Posted to '+ get_blog.blog_name,"success")
			return redirect(url_for('post_blog'))
		logger.warning(current_user.username + " failed to post to blog")
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
			logger.info(current_user.username + " created a new blog with name "+p.blog_name)
			flash('Blog created.', 'success')
			return redirect(url_for('post_blog'))
		logger.warning(current_user.username + " failed to create a new blog")
	return render_template('create_blog.html', form=form)



@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
	try:
		post = Posts.query.get_or_404(post_id)
		return render_template('post_page.html', post=post)
	except :
		logger.error(current_user.username + " tried to access a non-existing post.")
		flash('This post does not exist.', 'danger')
		return redirect(url_for('home'))
	

@app.route('/delete_post', methods=['GET', 'POST'])
@login_required
def delete_post():
	try:
		data=request.form['id']
		Posts.query.filter_by(id=data).delete()
		db.session.commit()
		logger.info(current_user.username + " deleted a post.")
		return jsonify()
	except:
		logger.critical(current_user.username + " tried to use delete route.")
		flash('You dont have permission to access this route', 'danger')
		return redirect(url_for('home'))

@app.route("/posted/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update(post_id):
	form = PostForm()
	try:
		post = Posts.query.get_or_404(post_id)
	except :
		logger.error(current_user.username + " tried to update a non-existing post.")
		flash('This post does not exist to update.', 'danger')
		return redirect(url_for('posted'))
	try:
		if post.author !=current_user.username:
			abort(403)
	except:
		logger.error(current_user.username +" tried to update "+ post.author + "'s post")
		flash('You tried to update another users post', 'danger')
		return redirect(url_for('posted'))
		
	
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		logger.info(current_user.username + " updated a post.")
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
	blogs=Blog.query.whoosh_search(request.args.get('query')).filter(Blog.user_id != current_user.id).all()
	if request.args.get('query'):
		blogs=Blog.query.whoosh_search(request.args.get('query')).filter(Blog.user_id != current_user.id).all()
		if not blogs:
			logger.warning(current_user.username + " failed to search for a blog.")
			flash('No blogs were found.', 'danger')
	return render_template('view_blogs.html', blogs = blogs)

@app.route('/follow', methods=['GET', 'POST'])
@login_required
def follow():
	try:
		flag=0
		data=request.form['id']
		clicked_blog=Blog.query.filter_by(id=data).first()
		blogs=current_user.followed_blogs
		for blog in blogs:
			if blog==clicked_blog:
				logger.info(current_user.username + " unfollowed a blog named "+ clicked_blog.blog_name)
				clicked_blog.user_followers.remove(current_user)
				flag=1
				break

		if flag==0:
			logger.info(current_user.username + " followed a blog named "+ clicked_blog.blog_name)
			clicked_blog.user_followers.append(current_user)
		db.session.commit()

		return jsonify()
	except:
		logger.critical(current_user.username + " tried to use follow route.")
		flash('You dont have permission to access this route', 'danger')
		return redirect(url_for('home'))
	

@app.route('/like', methods=['GET', 'POST'])
@login_required
def like():
	try:
		flag=0
		data=request.form['id']
		like_post=Posts.query.filter_by(id=data).first()
		posts=current_user.liked_posts
		for post in posts:
			if post==like_post:
				logger.info(current_user.username + " unliked a post")
				like_post.user_likes.remove(current_user)
				flag=1
				break

		if flag==0:
			logger.info(current_user.username + " liked a post")
			like_post.user_likes.append(current_user)
		db.session.commit()

		return jsonify()
	except:
		logger.critical(current_user.username + " tried to use like route.")
		flash('You dont have permission to access this route', 'danger')
		return redirect(url_for('home'))

@app.route('/general', methods=['GET', 'POST'])
@login_required
def general():
	posts=Posts.query.order_by(Posts.date.desc()).join(Blog).filter(Blog.user_id != current_user.id).all()
	return render_template('general.html', title='General', posts = posts)

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
	if not current_user.is_authenticated:
		redirect('index.html')
	else:
		f_blog=current_user.followed_blogs
		blogs = Blog.query.filter(Blog.user_followers.any(id=current_user.id)).all()
		li=[]
		for i in blogs:
			l=i.posts
			for pp in l:
				li.append(pp)

		da=sorted(li,key=lambda post: post.date,reverse=True)
		return render_template('home.html', title='home', p= da)
	return render_template('index.html', title='home')

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()

	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			if bcrypt.check_password_hash(user.password,form.password.data):
				login_user(user,remember=form.remember.data)
				logger.info(user.username+" just logged in")
				return redirect(url_for('home'))
			logger.warning(user.username+" failed to login.")
		flash('Incorrect username or password. Please try again.','danger')
		logger.warning("An attempt to login has failed .")
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
			logger.info("An account has been created with username: "+new_user.username)
			flash("Your account has been created! You can now login","success")
			return redirect(url_for('login'))
		logger.warning("A failed registeration attempt has occured.")
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
		logger.info(user.username+" has changed password.")
		return redirect(url_for('home'))
	else:
		logger.info(current_user.username+" failed to change his password.")
	return render_template('reset_password.html',form=form)

@app.route('/account')
@login_required
def account():
	total_posts=0
	total_followers=0
	total_likes=0
	blogs=Blog.query.filter_by(user_id=current_user.id).all()
	for blog in blogs:
		total_posts=total_posts+len(blog.posts)
		total_followers=total_followers+blog.user_followers.count()
		for posts in blog.posts:
			total_likes=total_likes+posts.user_likes.count()
	return render_template('account.html',posts_number=total_posts,total_followers=total_followers,total_likes=total_likes)

@app.route('/logout')
@login_required
def logout():
	logger.info(current_user.username+" logged out.")
	logout_user()
	return redirect(url_for("login"))

if __name__=='__main__':
	app.run(debug=True)