from itertools import product
from flask import Flask, jsonify
from flask import render_template, redirect, url_for, request, session
import re
from flask_mysqldb import MySQL
import MySQLdb


# Initialize flask application
app = Flask(__name__)


# App configuration for image
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database Configuration
app.config['SECRET_KEY'] = 'sdklaskdlask'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kakashi_2021'
app.config['MYSQL_DB'] = 'myshop'


mysql = MySQL(app)
# End of database configuration



# Start of the views functions
# Home view

@app.route("/")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''
            SELECT distinct category FROM ProductDetails
        '''
    )
    categories = cursor.fetchall()
    return render_template('index.html', categories=categories)

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
        cursor.execute('SELECT * FROM Customer WHERE  email = %s and password = %s', (email, password, ))
   

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

############################################################################

############################################################################

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
        cursor.execute('SELECT * FROM Customer WHERE username = %s', (username, ))
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
            cursor.execute('INSERT INTO Customer (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
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
        country = request.form['country']
        zipcode = request.form['zipcode']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('INSERT INTO CustomerDetails VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (user_id, cvv, creditCardNum, expiryDate, city, state, country, zipcode))
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

    return render_template('update_profile.html', msg=msg)


@app.route("/profile")
def userProfile():
    user_id = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        '''SELECT c.username, d.city, d.state, d.country
            FROM Customer as c
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
    # print(productID)
    
    cursor.execute(
        '''SELECT p.productCode, p.productName, d.description, p.price, d.weight, d.category 
        FROM Products AS p
        inner join ProductDetails AS d
        ON p.productCode = d.productCode
        WHERE p.productCode = %s
        ''', 
        (productID, )
    )
    products = cursor.fetchone()
    # print(products)
    return render_template('product-details.html', products=products)
#     # return render_template('product-details.html')


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
            SELECT distinct p.productName, p.price, d.description, d.inStock, d.weight, d.category
            FROM ProductDetails AS d
            INNER JOIN Products AS p
            ON d.productCode = p.productCode
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
                on p.productCode = d.productCode
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



if __name__ == "__main__":
    app.run(debug = True)

