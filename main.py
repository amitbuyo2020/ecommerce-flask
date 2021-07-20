from itertools import product
from flask import Flask, jsonify
from flask import render_template, redirect, url_for, request, session
import re
from flask.helpers import flash
from flask_mysqldb import MySQL
import MySQLdb
import os
from werkzeug.utils import secure_filename

# Initialize flask application
app = Flask(__name__)


# App configuration for image
UPLOAD_FOLDER = '/home/amit/Desktop/Web/my ecommerce project/static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Database Configuration
app.config['SECRET_KEY'] = 'sdklaskdlask'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kakashi_2021'
app.config['MYSQL_DB'] = 'nepali_bazaar'


mysql = MySQL(app)
# End of database configuration



# Start of the views functions
# Home view

@app.route("/")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''
           SELECT distinct d.category, p.productID, p.productName, p.price, p.productImg 
           FROM Products AS p
           INNER JOIN ProductDetails AS d
           on p.productID = d.productID
        '''
    )
    products = cursor.fetchall()
    return render_template('index.html', products=products)

############################ START OF AUTHENTICATION AND USER VIEWS ########################
# Login view
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Customers WHERE  email = %s and password = %s', (email, password, ))
   

        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['customerID']
            session['username'] = account['username']
            session['email'] = account['email']
            msg = "Logged in successfully"
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect email or password'
        
    return render_template('login.html', msg=msg)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Register view
@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    # Check to see if the request is post or get request
    if request.method == "POST" and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # create a mysql database cursor to get mysql functionalities
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Execute a mysql query to get the username and password of the user instance
        cursor.execute('SELECT * FROM Customers WHERE username = %s', (username, ))
        # fetches one result that matches the username 
        account = cursor.fetchone()

        if account:
            # avoids the duplicate name of username
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # if email doesnot match the given regular expression
            msg = 'Invalid email address'
        
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Username must contain only alphanumeric values"
        
        elif not 'username' or not 'password' or not 'email':
            msg = "Please fill out the form !"
        
        else:
            cursor.execute('INSERT INTO Customers (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            msg = 'Account registered successfully !'
            return redirect(url_for('home'))
    
    elif request.method == "POST" or request.method == "GET":
        msg = 'Please fill out the form'
    
    return render_template('register.html', msg=msg)



@app.route('/profile-update', methods=['GET', 'POST'])
def update_profile():
    msg = ''
    user_id = session.get('id')
    
    if request.method == "POST" and user_id is not None:
        cvv = request.form['cvv']
        creditCardNum = request.form['creditCardNum']
        expiryDate = request.form['expiryDate']
        city = request.form['city']
        state = request.form['state']
        contact = request.form['contact']
        country = request.form['country']
        zipcode = request.form['zipcode']
        
        avatar = request.files['avatar']
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('''INSERT INTO CustomerDetails 
            (customerID, avatar, contact, creditCardNum, cvv, city, state, country, zipcode, expiryDate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
            (user_id, filename, contact, creditCardNum, cvv, city, state, country, zipcode, expiryDate, ))
            mysql.connection.commit()
            return redirect(url_for('home'))

        except:
            msg = '''Oops, Something went wrong!! 
                    Please try again
                    '''
    elif user_id is None:
        return redirect(url_for("login"))
    else:
        msg = "Please fill out the form"

    return render_template('update_profile.html', msg=msg, filename=filename)



@app.route("/profile")
def userProfile():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''SELECT c.username, d.city, d.state, d.country, d.avatar
            FROM Customers as c
            inner join CustomerDetails as d 
            on c.customerID = d.customerID
            where c.customerID = %s
        ''',
        (user_id, )
    )
    profile = cursor.fetchone()
    if user_id is None:
        return redirect(url_for('login'))
    return render_template('profile.html', profile=profile)

######################## END OF AUTHENTICATIN AND USER VIEWS ########################################
############################################################################
# Seller Registration and login


@app.route('/seller/register', methods=['GET', 'POST'])
def register_as_seller():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['owner']
        password = request.form['password']
        businessName = request.form['businessName']
        registrationNum = request.form['registerNum']
        phone = request.form['phone']
        location = request.form['location']
        city = request.form['city']
        creditCardNum = request.form['creditCardNum']

        companyLogo = request.files['logo']
        filename = secure_filename(companyLogo.filename)
        companyLogo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Seller WHERE businessName = %s', (businessName, ))
        seller = cursor.fetchone()

        if seller:
            msg = "Seller with that name already exists"
        
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # if email doesnot match the given regular expression
            msg = 'Invalid email address'
        
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Username must contain only alphanumeric values"
        
        elif not 'username' or not 'password' or not 'email' or not 'businessName':
            msg = "Please fill out the form !"
        
        else:
            cursor.execute('''insert into Seller  (
                registrationNum,
                businessName ,
                owner ,
                email ,
                password ,
                phone ,
                creditCardNum ,
                location ,
                city, 
                img
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                (registrationNum, businessName, username, 
                    email, password, phone, creditCardNum, 
                    location, city, filename
                )
            )
            mysql.connection.commit()
            msg = 'Account registered successfully !'
            return redirect(url_for('seller_home'))
    else:
        msg = 'Please fill out the form'
    
    return render_template("seller-register.html", msg = msg)


@app.route("/seller/logout")
def logout_as_seller():
    msg = "Logging out means logging out"
    session.clear()
    return redirect(url_for('home'))


@app.route('/seller/login', methods=['POST', 'GET'])
def login_as_seller():
    msg = ''
    session.clear()
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Seller WHERE  email = %s and password = %s', (email, password, ))


        seller = cursor.fetchone()
        if seller:
            session['loggedin'] = True
            session['id'] = seller['sellerID']
            session['username'] = seller['owner']
            session['email'] = seller['email']
            msg = "Logged in successfully"
            print(session['id'], session['username'], session['email'], session['loggedin'])
            return redirect(url_for('seller_home'))
        else:
            msg = 'Incorrect email or password'
        
    return render_template('seller-login.html', msg=msg)

        
@app.route('/seller/')
def seller_home():
    seller_id = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if session['loggedin']:
        cursor.execute(
            '''
                SELECT * FROM Seller WHERE sellerID = %s
            ''',
            (seller_id, )
        )
        seller_info = cursor.fetchone()
        print(seller_info)


    return render_template('seller-home.html', seller_info=seller_info)




@app.route('/seller/profile')
def profile():
    if session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
                SELECT * FROM Seller
                WHERE sellerID = %s
            ''',
            (session['id'], )
        )
        seller = cursor.fetchone()
        # print(seller)
    else:
        return redirect(url_for('login_as_seller'))
    return render_template('seller-profile.html', seller=seller)


@app.route("/seller/add", methods=['GET', 'POST'])
def add_product():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(session['loggedin'])
    if request.method == "POST":
        # print(session['loggedin'])

        sellerID = session['id']
        productID = request.form['productID']
        productName = request.form['productName']
        price = request.form['price']
        weight = request.form['weight']
        ratings = request.form['ratings']
        description = request.form['description']
        category = request.form['category']
        inStock = request.form['inStock']

        productImg = request.files['productImg']
        filename = secure_filename(productImg.filename)
        productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute(
            '''
            INSERT INTO Products VALUES (%s, %s, %s, %s, %s)
            ''', 
            (productID, price, filename, productName, sellerID)
        )
        cursor.execute(
            '''
                INSERT INTO ProductDetails VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (productID, description, inStock, category, ratings, weight)
        )
        mysql.connection.commit()
        msg = "Product Added Successfully"
        return redirect(url_for('seller_home'))
    
    else:
        msg = "Something went wrong!!"
        # return redirect(url_for('login_as_seller'))
    return render_template('add_product.html', msg=msg)
################################END OF SELLER FUNCTIONS/ROUTES ############################################


######################## START OF PRODUCT VIEWS ###########################################
@app.route('/products')
def Products():
    cursor  = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''SELECT * FROM Products'''
    )
    products = cursor.fetchall()
    
    
    return render_template('products.html', products=products)


@app.route('/products/')
def product_details():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    productID = request.args.get('pk')

    
    cursor.execute(
        '''SELECT p.productID, p.productName, p.productImg, d.description, p.price, d.weight, d.category 
        FROM Products AS p
        inner join ProductDetails AS d
        ON p.productID = d.productID
        WHERE p.productID = %s
        ''', 
        (productID, )
    )
    products = cursor.fetchone()

    return render_template('product-details.html', products=products)



@app.route('/category/')
def category():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''
            SELECT distinct category FROM ProductDetails
        '''
    )
    categories = cursor.fetchall()
    print(categories)


    return render_template('categories.html', categories=categories)



@app.route('/category-list/')
def category_list():
    # print(request.args.get(''))
    category = request.args.get('cat')
    print(category)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''
            SELECT distinct p.productName, p.productImg,  p.price, d.description, d.inStock, d.weight, d.category
            FROM ProductDetails AS d
            INNER JOIN Products AS p
            ON d.productID = p.productID
            WHERE d.category = %s
        ''', 
        (category, )
    )
    cat_items = cursor.fetchall()
    print(cat_items)
    return render_template('cat_items.html', cat_items=cat_items)



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        items = request.form['product']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
                SELECT p.productName, p.price, d.description
                FROM Products AS p
                INNER JOIN ProductDetails AS d
                on p.productID = d.productID
                WHERE p.productName LIKE "%s"
            ''',
            (items, )
        )
        print(items)
        product = cursor.fetchall()
        print(product)
        return render_template('search.html', product=product)
    else:
        pass
    return render_template('search.html')
########################## END OF PRODUCT VIEWS ##################################################################

################################### START OF ORDER VIEWS ###############################
@app.route('/order', methods=["POST", 'GET'])
def order():
    if request.method == "POST":
        pass
################################### END OF ORDER VIEWS ###############################

if __name__ == "__main__":
    app.run(debug = True)

