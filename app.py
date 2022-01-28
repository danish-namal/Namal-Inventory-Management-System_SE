import os
import MySQLdb
from flask_mysqldb import MySQL
from flask import Flask, app, render_template, request, redirect, url_for, session, current_app
import secrets
from datetime import timedelta, datetime
import MySQLdb.cursors
import requests
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import webbrowser
import numpy as np


app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'NUIMS'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

mysql = MySQL(app)
date = datetime.now()
date = date.strftime("%d/%m/%y")

Username = ''
# Main Page Route
@app.route("/")
def index():
    return render_template('index.html')

# For saving images in db
def save_images(photo):
    hash_photo = secrets.token_urlsafe(10)
    _, file_extention = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extention
    file_path = os.path.join(current_app.root_path,'static/images/profile_pics', photo_name)
    photo.save(file_path)
    return photo_name

def product_images(photo):
    hash_photo = secrets.token_urlsafe(10)
    _, file_extention = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extention
    file_path = os.path.join(current_app.root_path,
                             'static/images/product_pics', photo_name)
    photo.save(file_path)
    return photo_name

# Registration Route
@app.route('/index.html', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['password'] != userDetails['cpassword']:
            return render_template("index.html", err="Did Not Register Because Passwords is not matched. Please enter Password Again.")
        else:
            # userDetails = request.form
            firstname = userDetails['firstname']
            lastname = userDetails['lastname']
            username = userDetails['username']
            email = userDetails['email']
            password = userDetails['password']
            designation = userDetails['designation']
            userImage = request.files
            profile_pic = save_images(userImage['pic'])
            # print(profile_pic)
            cur = mysql.connection.cursor()
            sql = "select * from users where email = %s"
            cur.execute(sql, [(email)])
            results = cur.fetchall()
            
            print(results)
            if results:
                for i in results:
                    # print(i)
                    return render_template("index.html", err="Didn't Registered Because Email Already Exists Please Enter Another Email.")
            else:
                cur.execute(
                    """INSERT INTO
                                users ( id, firstname,  lastname, username,  email, designation,  pass, picture ) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)""", (firstname, lastname, username, email, designation, password, profile_pic))
                mysql.connection.commit()
                cur.close()
    return render_template('index.html')

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['email'] == "":
            return render_template("index.html", id="login", err="Please Enter an Email.")
        elif userDetails['password'] == "":
            return render_template("index.html", id="login", err="Please Enter A Password.")
        else:
            email = userDetails['email']
            if email == "jawad2019@namal.edu.pk" or email == 'mzubair2019@namal.edu.pk' or email == 'manas2019@namal.edu.pk' or email == 'danish2019@namal.edu.pk' or email == 'sharjeel2019@namal.edu.pk':
                session["email"] = request.form.get("email")
                password = userDetails['password']
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "select * from users where email = %s and pass = %s"
                cur.execute(sql, [(email), (password)])
                results = cur.fetchone()
                if results:
                    session['loggedin'] = True
                    session['id'] = results['id']
                    return redirect(url_for("dashboard"))
                else:
                    return render_template('index.html', id="login", err="Email Or Password Is Not Found, Please Try Again")
            else:
                email = userDetails['email']
                session["email"] = request.form.get("email")
                password = userDetails['password']
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "select * from users where email = %s and pass = %s"
                cur.execute(sql, [(email), (password)])
                results = cur.fetchone()
                if results:
                    session['loggedin'] = True
                    session['id'] = results['id']
                    return redirect(url_for("userDashboard"))
                else:
                    return render_template('index.html', id="login", err="Email Or Password Is Not Found, Please Try Again")

    return render_template('index.html', id="login")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# Admin Dashboard Route
@app.route("/Admin_Dashboard/adminDashboard.html")
def dashboard():
    if 'loggedin' in session:
        api_key = "3f5dcdb66f841995d0cc10418c57a923"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + api_key + "&q=" + 'Mianwali'
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature = current_temperature - 273.15
            current_temperature = np.round(current_temperature-4)
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * from issueProducts")
        result = cur.fetchall()

        email = []
        designation = []        
        product_name = []
        Image = []
        status = []
        for i in result:
            email.append(i[1])
            designation.append(i[5])
            product_name.append(i[2])
            Image.append(i[3])
            status.append(i[4])

        approval_data = list(zip(email, designation, product_name, Image, status))

        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        email = data['email']

        sql = "select * from items"
        cur.execute(sql)
        items = cur.fetchall()
        itemsCount=0
        for i in items:
            itemsCount+=1

        sql = "select * from issueProducts where productStatus = 0"
        cur.execute(sql)
        requestCount = cur.fetchall()
        RequestCount = 0
        for i in requestCount:
            RequestCount+=1

        sql = "select * from issueProducts where productStatus = 1"
        cur.execute(sql)
        approveCount = cur.fetchall()
        ApproveCount = 0
        for i in approveCount:
            ApproveCount+=1

        sql = "select * from users"
        cur.execute(sql)
        users = cur.fetchall()
        print(users)
        Users = 0
        for i in users:
            if i['designation']!='Admin':
                Users+=1
        return render_template('Admin_Dashboard/adminDashboard.html', userData=data, picture=image, date=date, current_temperature=current_temperature,
                        approval_data=approval_data,itemsCount=itemsCount,RequestCount=RequestCount,ApproveCount=ApproveCount,Users=Users)
    else:
        return redirect(url_for('login'))

@app.route("/approval",methods=['GET', 'POST'])
def approval():
    if request.method == "POST":
        details = request.form['values']
        data = details.strip('()')
        data = data.split(',')
        num1, num2 = data
        email=str(num1)
        email=email.replace("'", "")
        product=str(num2)
        product=product.strip()
        product=product.replace("'", "")
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "UPDATE issueProducts SET productStatus = 1  WHERE email = %s and productName = %s"
        cur.execute(sql, [(email), (product)])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('dashboard'))

@app.route("/User_Dashboard/userDashboard.html")
def userDashboard():
    if 'loggedin' in session:
        api_key = "3f5dcdb66f841995d0cc10418c57a923"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + api_key + "&q=" + 'Mianwali'
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature = current_temperature - 273.15
            current_temperature = np.round(current_temperature-4)
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']
        email = data['email']

        sql = "select * from issueProducts where email = %s"
        cur.execute(sql, [(email)])
        issurItem = cur.fetchall()
        prod_name = []
        prdImage = []        
        Status = []
        for i in issurItem:
            prod_name.append(i['productName'])
            prdImage.append(i['Image'])
            if i['productStatus'] == 0:
                Status.append(0)
            else:
                Status.append(1)
        itemsToShow = list(zip(prod_name, prdImage, Status))   
        sql = "select * from items"
        cur.execute(sql)
        items = cur.fetchall()
        itemsCount=0
        for i in items:
            itemsCount+=1

        sql = "select * from issueProducts where email = %s"
        cur.execute(sql, [(email)])
        issueCount = cur.fetchall()
        IssueCount=0
        for i in issueCount:
            IssueCount+=1
        
        return render_template('User_Dashboard/userDashboard.html', userData=data, picture=image, date=date, current_temperature=current_temperature,
                            itemsToShow=itemsToShow, itemsCount=itemsCount, issueCount= IssueCount)
    else:
        return redirect(url_for('login'))


@app.route("/User_Dashboard/products/products_cat.html", methods=['GET', 'POST'])
def userProducts():
    if 'loggedin' in session:
            if request.method == 'POST':
                itemDetails = request.form
                itemId = itemDetails['values']
                itemId = int(itemId)

                Id = session['id']
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "select * from users where id = %s"
                cur.execute(sql, [(Id)])
                data = cur.fetchone()
                image = data['picture']
                email= data['email']
                designation = data['designation']


                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "select * from items where item_id = %s"
                cur.execute(sql, [(itemId)])
                res = cur.fetchone()
                status=0
                cur = mysql.connection.cursor()
                cur.execute( """INSERT INTO issueProducts (id, email, productName,  Image, productStatus,designation ) VALUES (NULL,%s,%s,%s,%s,%s)""", (email, res['item_name'], res['image'], status, designation))
                mysql.connection.commit()
                cur.close()

                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "select quantity from items where item_id = %s"
                cur.execute(sql, [(itemId)])
                Quantity = cur.fetchone()
                temp = Quantity['quantity'] - 1

                sql = "UPDATE items SET quantity = %s  WHERE item_id = %s"
                cur.execute(sql, [(temp), (itemId)])
                mysql.connection.commit()
                cur.close()
   
            cur = mysql.connection.cursor()
            cur.execute("select * from items where category_name = 'Sports'")
            sports = cur.fetchall()
            cur.execute("select * from items where category_name = 'ITSC'")
            itsc = cur.fetchall()
            cur.execute("select * from items where category_name = 'Medical'")
            medical = cur.fetchall()
            cur.execute(
                "select * from items where category_name = 'Decoration'")
            decor = cur.fetchall()
            Id = session['id']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select * from users where id = %s"
            cur.execute(sql, [(Id)])
            data = cur.fetchone()
            image = data['picture']

            prdImage = []
            name = []
            quantity = []
            Id = []
            for i in sports:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
                Id.append(i[0])
            Sports = list(zip(name, quantity, prdImage, Id))

            prdImage = []
            name = []
            quantity = []
            Id = []
            for i in itsc:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
                Id.append(i[0])
            Itsc = list(zip(name, quantity, prdImage, Id))

            prdImage = []
            name = []
            quantity = []
            Id = []
            for i in medical:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
                Id.append(i[0])
            Medical = list(zip(name, quantity, prdImage, Id))

            prdImage = []
            name = []
            quantity = []
            Id = []
            for i in decor:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
                Id.append(i[0])
            Decor = list(zip(name, quantity, prdImage, Id))

            return render_template('/User_Dashboard/products/products_cat.html', picture=image, Sports=Sports,
                                    Itsc=Itsc, Medical=Medical, Decor=Decor)
    else:
        return redirect(url_for('login'))

@app.route("/User_Dashboard/userProfile/userDetails.html")
def userDetail():
    if 'loggedin' in session:
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']
        return render_template('/User_Dashboard/userProfile/userDetails.html', userData=data, picture=image, date=date)
    else:
        return redirect(url_for('login'))


@app.route("/User_Dashboard/displayProducts/showAllProducts.html")
def userShowAllProducts():
    if 'loggedin' in session:
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']

        cur = mysql.connection.cursor()
        cur.execute("select * from items")
        products = cur.fetchall()

        prdImage = []
        name = []
        quantity = []
        num = []
        category = []
        for i in products:

            prdImage.append(i[3])
            name.append(i[1])
            quantity.append(i[2])
            num.append(i[0])
            category.append(i[4])
        allProducts = list(zip(num, name, quantity, prdImage, category))

        return render_template('/User_Dashboard/displayProducts/showAllProducts.html', picture=image, allProducts=allProducts)
    else:
        return redirect(url_for('login'))

@app.route("/Admin_Dashboard/userManagement/user_Management.html")
def userManagement():
    if 'loggedin' in session:
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']

        sql = "select * from users"
        cur.execute(sql)
        users = cur.fetchall()
        Users = 0
        for i in users:
            if i['designation']!='Admin':
                Users+=1

        userName = []
        email = []
        designation = []
        for i in users:
            fullName= i['firstName'] +' '+ i['lastName']
            userName.append(fullName)     
            email.append(i['email'])
            designation.append(i['designation'])
        allUsers = list(zip(userName, email, designation))

        return render_template('/Admin_Dashboard/userManagement/user_Management.html', picture=image, date=date, userCount=Users, allUsers=allUsers)
    else:
        return redirect(url_for('login'))

@app.route("/Admin_Dashboard/products/products_cat.html")
def Products():
    if 'loggedin' in session:
        if request.method == 'GET':
            itemDetails = request.form
            cur = mysql.connection.cursor()
            cur.execute("select * from items where category_name = 'Sports'")
            sports = cur.fetchall()
            cur.execute("select * from items where category_name = 'ITSC'")
            itsc = cur.fetchall()
            cur.execute("select * from items where category_name = 'Medical'")
            medical = cur.fetchall()
            cur.execute(
                "select * from items where category_name = 'Decoration'")
            decor = cur.fetchall()
            Id = session['id']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select * from users where id = %s"
            cur.execute(sql, [(Id)])
            data = cur.fetchone()
            image = data['picture']
            prdImage = []
            name = []
            quantity = []
            for i in sports:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
            Sports = list(zip(name, quantity, prdImage))
            prdImage = []
            name = []
            quantity = []
            for i in itsc:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
            Itsc = list(zip(name, quantity, prdImage))
            prdImage = []
            name = []
            quantity = []
            for i in medical:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
            Medical = list(zip(name, quantity, prdImage))
            prdImage = []
            name = []
            quantity = []
            for i in decor:
                prdImage.append(i[3])
                name.append(i[1])
                quantity.append(i[2])
            Decor = list(zip(name, quantity, prdImage))
            return render_template('/Admin_Dashboard/products/products_cat.html', picture=image, Sports=Sports,
                                   Itsc=Itsc, Medical=Medical, Decor=Decor)
        else:
            Id = session['id']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select * from users where id = %s"
            cur.execute(sql, [(Id)])
            data = cur.fetchone()
            image = data['picture']
            return render_template('/Admin_Dashboard/products/products_cat.html', picture=image)
    else:
        return redirect(url_for('login'))

@app.route("/Admin_Dashboard/displayProducts/showAllProducts.html")
def showAllProducts():
    if 'loggedin' in session:
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']

        cur = mysql.connection.cursor()
        cur.execute("select * from items")
        products = cur.fetchall()

        prdImage = []
        name = []
        quantity = []
        num = []
        category = []
        for i in products:
            prdImage.append(i[3])
            name.append(i[1])
            quantity.append(i[2])
            num.append(i[0])
            category.append(i[4])
        allProducts = list(zip(num, name, quantity, prdImage, category))

        return render_template('/Admin_Dashboard/displayProducts/showAllProducts.html', picture=image, allProducts=allProducts)
    else:
        return redirect(url_for('login'))

@app.route("/Admin_Dashboard/addProducts/add_products.html", methods=['GET', 'POST'])
def addProducts():
    if 'loggedin' in session:
        if request.method == 'POST':
            itemDetails = request.form
            itemName = itemDetails['itemName']
            quantity = itemDetails['quantity']
            productImage = request.files
            product_pic = product_images(productImage['pic'])
            print(product_pic)
            categoryName = itemDetails['categoryName']
            cur = mysql.connection.cursor()
            cur.execute(
                """INSERT INTO items (item_id, item_name, quantity,image,category_name ) VALUES (NULL, %s, %s, %s, %s)""",(itemName, quantity, product_pic, categoryName))
            mysql.connection.commit()
            cur.close()
            Id = session['id']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select * from users where id = %s"
            cur.execute(sql, [(Id)])
            data = cur.fetchone()
            image = data['picture']
            return render_template('/Admin_Dashboard/addProducts/add_products.html', picture=image)
        else:
            Id = session['id']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "select * from users where id = %s"
            cur.execute(sql, [(Id)])
            data = cur.fetchone()
            image = data['picture']
            return render_template('/Admin_Dashboard/addProducts/add_products.html', picture=image)
    else:
        return redirect(url_for('login'))

@app.route("/Admin_Dashboard/userProfile/userDetails.html")
def adminDetail():
    if 'loggedin' in session:
        Id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from users where id = %s"
        cur.execute(sql, [(Id)])
        data = cur.fetchone()
        image = data['picture']
        return render_template('/Admin_Dashboard/userProfile/userDetails.html', userData=data, picture=image, date=date)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
