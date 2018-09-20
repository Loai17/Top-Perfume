# -*- coding: utf-8 -*-
from flask import *
from flask import session as login_session
from sqlalchemy.exc import IntegrityError
from model import *
from werkzeug.utils import secure_filename
from forms import ContactForm
import json, ast
import pyperclip
import datetime
import os

# Flask Mail
from flask_mail import Message, Mail

mail = Mail()

UPLOAD_FOLDER = 'static/productsImages'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.secret_key = "MY_SUPER_SECRET_KEY"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'topperfum1@gmail.com'
app.config["MAIL_PASSWORD"] = 'Blackisblack212'

mail.init_app(app)

# LOCAL
engine = create_engine('sqlite:///database.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def autoBrand():
	products = session.query(ShopItems).all()
	brands=[]
	for product in products:
		flag=True
		for brand in brands:
			if brand == product.brand:
				flag=False
		if flag:
			brands.append(product.brand)

	if brands == []:
		brands = [""]
		print ("Sorry about that. Looks like you don't have any products yet.")
	return brands


@app.route('/',methods=['GET','POST'])
def home():
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False
	brands = ast.literal_eval(json.dumps(autoBrand()))

	products=[]
	if len(productsList) >= 8:
		for i in range(8) :
			products.append(productsList[i])
	else:
		products = productsList

	if len(products)<len(productsList) :
		loadMore = True

	if request.method == 'POST':
		form.name = request.form['name']
		form.email = request.form['email']
		form.message = request.form['message']
		
		if form.name != "" and form.email!= "" and form.message != "":
			msg = Message("Top Perfum Message", sender='TopPerfum1@gmail.com', recipients=['topperfum1@gmail.com'])
			msg.body = """
			From: %s <%s>
			Message: %s
			""" % (form.name, form.email, form.message)
			mail.send(msg)
			print("message sent")

			return render_template('index.html', success=True, form=form ,number=1, products=products, loadMore=loadMore, brands=brands)
		else :
			return render_template('index.html', form=form ,number=1, products=products, loadMore=loadMore, brands=brands)


	return render_template('index.html', form=form ,number=1, products=products, loadMore=loadMore, brands=brands)


@app.route('/<number>', methods=['GET','POST'])
def loadMore(number):
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False
	brands = ast.literal_eval(json.dumps(autoBrand()))

	products=[]
	if len(productsList) >= (8 * int(number)) :
		for i in range(8* int(number)) :
			products.append(productsList[i])
	else:
		products = productsList

	if len(products)<len(productsList) :
		loadMore = True

	if request.method == 'POST':
		if form.validate() == False:
			flash('All fields are required.')
			return render_template('index.html', form=form, number=int(number), products=products, loadMore=loadMore, brands=brands)
		else:
			msg = Message("Website Message", sender='contactUs@example.com', recipients=['loai.qubti@gmail.com'])
			msg.body = """
			From: %s <%s>
			Message: %s
			""" % (form.name.data, form.email.data, form.message.data)
			mail.send(msg)

			return render_template('index.html', success=True, form=form, number=int(number), products=products, loadMore=loadMore, brands=brands)
		
	return render_template('index.html', form=form, number=int(number), products=products, loadMore=loadMore, brands=brands)

@app.route('/subscribe', methods=['POST'])
def subscribe():
	if request.form['email'] != "":
		email = Emails(email=request.form['email'])
		session.add(email)
		session.commit()
	return redirect(url_for('home'))

@app.route('/shop', methods=['GET','POST'])
def shop():
	products = session.query(ShopItems).all()
	brands = ast.literal_eval(json.dumps(autoBrand()))
	return render_template('shop.html' , products = products,brands = brands)

@app.route('/about', methods=['GET','POST'])
def about():
	brands = ast.literal_eval(json.dumps(autoBrand()))
	return render_template('about.html',brands=brands)

@app.route('/product/<id>',methods=['GET','POST'])
def product(id):
	product = session.query(ShopItems).filter_by(id=id).one()
	brands = ast.literal_eval(json.dumps(autoBrand()))

	covers = product.images.split(",")
	
	cover1 = covers[0]
	cover2 = covers[1]
	cover3 = covers[2]

	reviews = session.query(Reviews).filter_by(shopItemID=id).all()
	starAverage = 0;
	starSum = 0;
	starCounter = 0;

	for review in reviews:
		starSum += review.rating

	if(starSum>0):
		starAverage = starSum/len(reviews);

	allProducts= session.query(ShopItems).all()
	relatedProducts=[]
	for p in allProducts:
		if p.brand == product.brand:
			if p.id!=product.id:
				relatedProducts.append(p)

	return render_template('product.html' , product=product,brands=brands,cover1=cover1,cover2=cover2,cover3=cover3, reviews=reviews,averageRating=starAverage,reviewsNum=len(reviews),relatedProducts=relatedProducts)

@app.route('/feedback/<productId>', methods=['GET','POST'])
def feedback(productId):
	if request.method == "POST":
		date = str(datetime.datetime.now().day) + "/" + str(datetime.datetime.now().month) + "/" + str(datetime.datetime.now().year)
		name = request.form['name']
		email = request.form['email']
		rating = request.form['rating']
		review = request.form['review']
		shopItemId = productId

		feedback = Reviews(name=name,email=email,date=date,rating=rating,review=review,shopItemID=shopItemId)
		session.add(feedback)
		session.commit()

		return redirect(url_for('product',id=productId))
	return redirect(url_for('product',id=productId))

@app.route('/search',methods=['GET','POST'])
def search():
	if request.method == "POST":
		searchedFor1 = request.form['search']
		searchedForList = searchedFor1.split()
		print(searchedForList)

		products = session.query(ShopItems).all()
		productsIdFound = []

		for word in searchedForList:
			for product in products:
				if (product.name.lower()).find(word.lower()) != -1:
					print ("found " + product.name + " by name")
					if(product.id in productsIdFound):
						print("It's already in")
					else:
						productsIdFound.append(product.id)
						print("Appended " + product.name)
				elif (product.description.lower()).find(word.lower()) != -1:
					print ("found " + product.name + " by description")
					if(product.id in productsIdFound):
						print("It's already in")
					else:
						productsIdFound.append(product.id)
						print("Appended " + product.name)
				elif (product.brand.lower()).find(word.lower()) != -1:
					print ("found " + product.name + " by brand")
					if(product.id in productsIdFound):
						print("It's already in")
					else:
						productsIdFound.append(product.id)
						print("Appended " + product.name)
				else:
					print ("found none")

		return redirect(url_for('searchResults',productsIdFound=productsIdFound))

@app.route('/results/<productsIdFound>',methods=['GET','POST'])
def searchResults(productsIdFound):
	productsFound = []

	for idNum in productsIdFound:
		prodTemp = session.query(ShopItems).filter_by(id=idNum).first()
		productsFound.append(prodTemp)


	brands = ast.literal_eval(json.dumps(autoBrand()))
	return render_template('shop.html' , products = productsFound,brands = brands)


# Admin Portal
@app.route('/admin',methods=['GET','POST'])
def adminSignin():
	if 'idAdmin' in login_session:
		admin = session.query(Admin).filter_by(id=login_session['idAdmin']).one()
		return redirect(url_for('admin'))

	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		
		adminCheck=session.query(Admin).filter_by(username=username).first()

		if(adminCheck != None and adminCheck.password==password):
			# Logged in successfully
			login_session['idAdmin'] = adminCheck.id
			return redirect(url_for('admin'))
		else:
			return redirect(url_for('adminSignin'))
	else:
		return render_template('adminSignin.html')


@app.route('/admin-panel-secret-login', methods=['GET','POST'])
def admin():
	if 'idAdmin' in login_session:
		emails = session.query(Emails).all()
		products = session.query(ShopItems).all()
		allReviews = session.query(Reviews).all()

		# products = []  # list of products
		# for product in session.query(ShopItems).all():
		# 	products.append(product.encode('utf-8'))

		if request.method== 'POST':
			return render_template('admin.html', products=products, emails=emails, reviews=allReviews)
		return render_template('admin.html' , products=products, emails=emails , reviews=allReviews)
	else:
		return redirect(url_for('adminSignin'))


@app.route('/addProduct', methods=['GET','POST'])
def addProduct():
	if 'idAdmin' in login_session:
		brands = ast.literal_eval(json.dumps(autoBrand()))

		if request.method == 'POST':
			name = request.form['name']
			gender = request.form['gender']
			brand = request.form['brand']
			price = request.form['price']
			description = request.form['description']
			thumbnail = request.files['thumb'].filename
			images = request.files['cover1'].filename+","+request.files['cover2'].filename+","+request.files['cover3'].filename

			product = ShopItems(name=name,gender=gender,brand=brand,description=description,price=price,thumbnail=thumbnail,images=images)
			
			thumbPic=request.files['thumb']
			coverPic1=request.files['cover1']
			coverPic2=request.files['cover2']
			coverPic3=request.files['cover3']
			
			if thumbPic and allowed_file(thumbPic.filename) and coverPic1 and allowed_file(coverPic1.filename) and coverPic2 and allowed_file(coverPic2.filename) and coverPic3 and allowed_file(coverPic3.filename):
				# thumb_name = "1_" + secure_filename(thumb.filename)
				# cover_name = "1_" + secure_filename(cover.filename)
				thumbPic.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(thumbPic.filename)))
				coverPic1.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic1.filename)))
				coverPic2.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic2.filename)))
				coverPic3.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic3.filename)))

				session.add(product)
				session.commit()

				return redirect(url_for('admin'))
			else:
				return None

		return render_template('AddEditProduct.html', brands=brands)
	return redirect(url_for('adminSignin'))


@app.route('/editProduct/<id>', methods=['GET','POST'])
def editProduct(id):
	if 'idAdmin' in login_session:
		product = session.query(ShopItems).filter_by(id=id).one()
		brands = ast.literal_eval(json.dumps(autoBrand()))

		if request.method == 'POST':
			name = request.form['name']
			gender = request.form['gender']
			brand = request.form['brand']
			price = request.form['price']
			description = request.form['description']
			thumbnail = request.files['thumb'].filename
			cover1=request.files['cover1'].filename
			cover2=request.files['cover2'].filename
			cover3=request.files['cover3'].filename

			originalCovers = product.images.split(",")

			cover1original = originalCovers[0] 
			cover2original = originalCovers[1] 
			cover3original = originalCovers[2] 

			if thumbnail == "":
				print ("Thumbnail is not changed")
			else:
				thumbPic=request.files['thumb']
				if thumbPic and allowed_file(thumbPic.filename):
					thumbPic.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(thumbPic.filename)))
					product.thumbnail=thumbnail
				else:
					print("שם התמונה לא יתקבל", "אנא שנה את שם הקובץ של תמונת החוצה בבקשה.")

			if cover1 == "":
				print ("Cover1 is not changed")
				images = cover1original
			else:
				coverPic1=request.files['cover1']
				if coverPic1 and allowed_file(coverPic1.filename):
					coverPic1.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic1.filename)))
					images = cover1
				else:
					print("שם התמונה לא יתקבל", "אנא שנה את שם הקובץ של תמונה(1) בבקשה.")

			if cover2 == "":
				print ("Cover2 is not changed")
				images = images+","+cover2original
			else:
				coverPic2=request.files['cover2']
				if coverPic2 and allowed_file(coverPic2.filename):
					coverPic2.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic2.filename)))
					images = images+","+cover2
				else:
					print("שם התמונה לא יתקבל", "אנא שנה את שם הקובץ של תמונה(2) בבקשה.")

			if cover3 == "":
				print ("Cover3 is not changed")
				images = images+","+cover3original
			else:
				coverPic3=request.files['cover3']
				if coverPic3 and allowed_file(coverPic3.filename):
					coverPic3.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(coverPic3.filename)))
					images = images+","+cover3
				else:
					tkMessageBox.showinfo("שם התמונה לא יתקבל", "אנא שנה את שם הקובץ של תמונה(3) בבקשה.")

			newBrand = request.form['brandOther']

			if request.form['brand'] != "noChange":
				if newBrand!="":
					brand = newBrand 
				product.brand=brand

			product.name=name
			product.gender=gender
			product.price=price
			product.description=description
			product.images=images
			session.commit()

			return redirect(url_for('admin'))

		return render_template('AddEditProduct.html' , edit=True, product=product,brands=brands)
	return redirect(url_for('adminSignin'))

@app.route('/deleteProduct/<id>', methods=['GET','POST'])
def deleteProduct(id):
	if 'idAdmin' in login_session:
		product = session.query(ShopItems).filter_by(id=id).one()

		session.delete(product)
		session.commit()

	return redirect(url_for('admin'))	

@app.route('/deleteEmail/<id>', methods=['GET','POST'])
def deleteEmail(id):
	if 'idAdmin' in login_session:
		email = session.query(Emails).filter_by(id=id).one()

		session.delete(email)
		session.commit()

	return redirect(url_for('admin'))	

@app.route('/deleteReview/<id>', methods=['GET','POST'])
def deleteReview(id):
	if 'idAdmin' in login_session:
		review = session.query(Reviews).filter_by(id=id).one()

		session.delete(review)
		session.commit()

	return redirect(url_for('admin'))	


@app.route('/logout', methods=['GET','POST'])
def logout():
	if 'idAdmin' in login_session:
		del login_session['idAdmin']
	return redirect(url_for('adminSignin'))

@app.route('/copyEmails',methods=['GET','POST'])
def copyEmails():
	if 'idAdmin' in login_session:
		emails = session.query(Emails).all()

		emailsList=[]
		for email in emails:
			emailsList.append(str(email.email))

		emailsToCopy = ",".join(emailsList)

		pyperclip.copy(emailsToCopy)

		return redirect(url_for('admin'))
	else:
		return redirect(url_for('adminSignin'))



if __name__ == '__main__':
	app.run(debug=True)
