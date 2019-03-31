# -*- coding: utf-8 -*-
import os
from flask import *
from flask import session as login_session
from sqlalchemy.exc import IntegrityError
from model import *
from werkzeug.utils import secure_filename
from forms import ContactForm
import json, ast
import pyperclip
import datetime

# Flask Mail
from flask_mail import Message, Mail

import dj_database_url

DATABASES = { 'default': dj_database_url.config(conn_max_age=None) }
DATABASES['default'] = dj_database_url.config(default='postgres://pulbxlzuwdqapw:6d2db8167c2b4442869a2ffdd9ad5bf048f4b44355ce2fb5b54ef39ee4504190@ec2-54-247-79-32.eu-west-1.compute.amazonaws.com:5432/dfqomvbf10gqne')
DATABASES['default'] = dj_database_url.parse('postgres://pulbxlzuwdqapw:6d2db8167c2b4442869a2ffdd9ad5bf048f4b44355ce2fb5b54ef39ee4504190@ec2-54-247-79-32.eu-west-1.compute.amazonaws.com:5432/dfqomvbf10gqne', conn_max_age=600)

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
engine = create_engine(os.environ['DATABASE_URL'])

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


def brandShow():
	products = session.query(ShopItems).all()
	brands=autoBrand()
	brandShow=[]
	p=None
	for brand in brands:
		for product in products:
			if product.brand == brand:
				p=product
		if p is not None:
			brandShow.append(p)

	if brandShow == []:
		brandShow = [""]
		print ("Sorry about that. Looks like you don't have any products yet.")
	return brandShow


@app.route('/',methods=['GET','POST'])
def home():
	form = ContactForm()

	loadMore = False
	# brands = ast.literal_eval(json.dumps(autoBrand()))
	brandShowList = session.query(Brands).all() #brandShow()#ast.literal_eval(json.dumps(brandShow()))
	varBrandShow=[]
	if len(brandShowList) >= 8:
		for i in range(8) :
			varBrandShow.append(brandShowList[i])
	else:
		varBrandShow = brandShowList

	if len(varBrandShow)<len(brandShowList) :
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

			return render_template('index.html', success=True, form=form ,number=1, brands=varBrandShow, loadMore=loadMore)
		else :
			return render_template('index.html', form=form ,number=1, brands=varBrandShow, loadMore=loadMore)


	return render_template('index.html', form=form ,number=1, brands=varBrandShow, loadMore=loadMore)


@app.route('/<number>', methods=['GET','POST'])
def loadMore(number):
	form = ContactForm()
	loadMore = False

	brandShowList = session.query(Brands).all() #brandShow()#ast.literal_eval(json.dumps(brandShow()))
	varBrandShow=[]

	products=[]
	if len(brandShowList) >= (8 * int(number)) :
		for i in range(8* int(number)) :
			varBrandShow.append(brandShowList[i])
	else:
		varBrandShow = brandShowList

	if len(varBrandShow)<len(brandShowList) :
		loadMore = True

	if request.method == 'POST':
		if form.validate() == False:
			flash('All fields are required.')
			return render_template('index.html', form=form, number=int(number), brands=varBrandShow, loadMore=loadMore)
		else:
			msg = Message("Top Perfum Message", sender='TopPerfum1@gmail.com', recipients=['topperfum1@gmail.com'])
			msg.body = """
			From: %s <%s>
			Message: %s
			""" % (form.name.data, form.email.data, form.message.data)
			mail.send(msg)

			return render_template('index.html', success=True, form=form, number=int(number), brands=varBrandShow, loadMore=loadMore)
		
	return render_template('index.html', form=form, number=int(number), brands=varBrandShow, loadMore=loadMore)

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
		if p.brand == product.brand or p.gender == product.gender:
			if p.id!=product.id:
				relatedProducts.append(p)

	return render_template('product.html' , product=product,brands=brands, reviews=reviews,averageRating=starAverage,reviewsNum=len(reviews),relatedProducts=relatedProducts)

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

@app.route('/search',methods=['GET','POST'])
def search():
	if request.method == "POST":
		searchedFor1 = request.form['search']
		searchedForList = searchedFor1.split()
		print("------------------"+ str(searchedForList)+"-------------------")

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

		IdString = ""
		for Id in productsIdFound:
			IdString = IdString+str(Id)+","

		return redirect(url_for('searchResults',productsIdFound=IdString))

@app.route('/by_brand/<name>',methods=['GET','POST'])
def search_brands(name):
	# if request.method == "POST":
	print("------------------ Gathering products by "+ name +" -----------------")

	products = session.query(ShopItems).all()
	productsIdFound = []

	for product in products:
		if (product.brand.lower() == name.lower()):
			print ("found " + product.name + " by brand")
			if(product.id in productsIdFound):
				print("It's already in")
			else:
				productsIdFound.append(product.id)
				print("Appended " + product.name)
		else:
			print ("found none")

	IdString = ""
	for Id in productsIdFound:
		IdString = IdString+str(Id)+","

	return redirect(url_for('searchResults',productsIdFound=IdString))


@app.route('/results/<productsIdFound>',methods=['GET','POST'])
def searchResults(productsIdFound):
	newList = productsIdFound.split(",")
	productsFound = []
	for idNum in newList:
		if(idNum!=''):
			prodTemp = session.query(ShopItems).filter_by(id=int(idNum)).first()
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
	
	return render_template('adminSignin.html')

def addBrands():
	brands = autoBrand()
	for brand in brands:
		new_brand = Brands(name=brand,logo="")
		session.add(new_brand)
	session.commit()

@app.route('/admin-panel-secret-login', methods=['GET','POST'])
def admin():
	if 'idAdmin' in login_session:
		emails = session.query(Emails).all()
		products = session.query(ShopItems).all()
		allReviews = session.query(Reviews).all()
		brands = session.query(Brands).all()
		# products = []  # list of products
		# for product in session.query(ShopItems).all():
		# 	products.append(product.encode('utf-8'))

		if request.method== 'POST':
			return render_template('admin.html', products=products, emails=emails, reviews=allReviews, brands=brands)
		return render_template('admin.html' , products=products, emails=emails , reviews=allReviews, brands=brands)
	else:
		return redirect(url_for('adminSignin'))


@app.route('/addProduct', methods=['GET','POST'])
def addProduct():
	if 'idAdmin' in login_session:
		brands = ast.literal_eval(json.dumps(autoBrand()))

		if request.method == 'POST':
			name = request.form['name']
			gender = request.form['gender']
			if request.form['brand']=="other":
				brand = request.form['brandOther']
			else:
				brand = request.form['brand']
			price = request.form['price']
			description = request.form['description']
			thumbnail = request.form['thumb']
			cover1=request.form['cover1']
			cover2=request.form['cover2']
			cover3=request.form['cover3']
			product = ShopItems(name=name,gender=gender,brand=brand,description=description,price=price,thumbnail=thumbnail,cover1=cover1,cover2=cover2,cover3=cover3)
			
			session.add(product)
			session.commit()
			return redirect(url_for('admin'))
		else:
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
			thumbnail = request.form['thumb']
			cover1=request.form['cover1']
			cover2=request.form['cover2']
			cover3=request.form['cover3']

			newBrand = request.form['brandOther']

			if request.form['brand'] != "noChange":
				if newBrand!="":
					brand = newBrand 
				product.brand=brand

			product.name=name
			product.gender=gender
			product.price=price
			product.description=description
			product.thumbnail=thumbnail
			product.cover1=cover1
			product.cover2=cover2
			product.cover3=cover3
			session.commit()

			return redirect(url_for('admin'))

		else:
			return render_template('AddEditProduct.html' , edit=True, product=product,brands=brands)
	else:
		return redirect(url_for('adminSignin'))

@app.route('/addBrand', methods=['GET','POST'])
def addBrand():
	if 'idAdmin' in login_session:
		if request.method == 'POST':
			name = request.form['name']
			logo = request.form['logo']
			
			brand = Brands(name=name,logo=logo)
			
			session.add(logo)
			session.commit()
			return redirect(url_for('admin'))
		else:
			return render_template('AddEditBrand.html',edit=False)
	else:
		return redirect(url_for('adminSignin'))

@app.route('/editBrand/<id>', methods=['GET','POST'])
def editBrand(id):
	if 'idAdmin' in login_session:
		brand = session.query(Brands).filter_by(id=id).one()

		if request.method == 'POST':
			name = request.form['name']
			logo = request.form['logo']

			brand.name=name
			brand.logo=logo
			session.commit()

			return redirect(url_for('admin'))

		else:
			return render_template('AddEditBrand.html', edit=True, brand=brand)
	else:
		return redirect(url_for('adminSignin'))

@app.route('/deleteProduct/<id>', methods=['GET','POST'])
def deleteProduct(id):
	if 'idAdmin' in login_session:
		product = session.query(ShopItems).filter_by(id=id).one()

		session.delete(product)
		session.commit()

	return redirect(url_for('admin'))	

@app.route('/deleteBrand/<id>', methods=['GET','POST'])
def deleteBrand(id):
	if 'idAdmin' in login_session:
		brand = session.query(Brands).filter_by(id=id).one()

		session.delete(brand)
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
