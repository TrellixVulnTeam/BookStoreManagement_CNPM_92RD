from __init__ import app
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from admin_models import *
from __init__ import login
from models import User
from flask_login import login_user, logout_user
import hashlib
import utils

from elasticsearch import Elasticsearch

import os
import urllib.request
from flask import flash, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/infoImage', methods=['get', 'post'])
def upload_image():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # print('upload_image filename: ' + filename)
    id = request.form.get("idUser")
    user = User.query.get(id)
    user.avatar = 'images/' + filename
    db.session.commit()
    return render_template('info.html')

@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='images/' + filename), code=301)


@app.route('/info')
def info():
    return render_template('info.html')


@app.route("/")
def index():
    return render_template('base/base.html',  list_book= utils.load_Book(), list_book_image=utils.load_book_image(), list_book_category=utils.get_book_category())

@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)


@app.route('/info', methods = ['get', 'post'])
def updateInfoUser():
    err_msg = ""
    if request.method == 'POST':
        id = request.form.get("idUser")
        user = User.query.get(id)
        user.lname = request.form.get("lname")
        user.fname = request.form.get("fname")
        user.birthday = request.form.get("birthday")
        user.phone = request.form.get("phone")
        user.address = request.form.get("address")

        db.session.commit()

        return jsonify({
            "message": "Sua thanh cong"
            # "cart": cart
        })


@app.route('/login', methods = ['get', 'post'])
def login_admin():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password", "")
        password = hashlib.md5(password.encode("utf-8")).hexdigest()
        user = User.query.filter(User.username == username, User.password == password).first()

        if user:
            flash('Logged in successfully.')
            login_user(user=user)
        else:
            flash("Login failed !", category='error')

    return redirect('/')

# @app.route('/1')
# def listBook():
#     return render_template('base/banner_bottom.html', list_book= utils.load_Book(), list_book_image=utils.load_book_image())

@app.route('/api/cart', methods=['get' , 'post'])
def add_to_cart():
    data = request.json
    id_book = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    id_cart, list_item = utils.list_item_of_user(1)

    flag = 0
    for item in list_item:
        if (str(item.idBook) == id_book):
            item.quantity += 1
            flag = 1
            db.session.commit()
    if (flag == 0):
        newitem = CartItem(idCart=id_cart, idBook=id_book, quantity=1, price=price, discount=price)
        db.session.add(newitem)
        db.session.commit()

    return jsonify({
        "message": "Them thanh cong"
    })


@app.route('/pay')
def payment():
    id_cart, list_item = utils.list_item_of_user(current_user.id)
    total_quantity, total_amount = utils.cart_stats(current_user.id)
    return render_template('payment.html', id_cart = id_cart, list_item = list_item, total_amount = total_amount, total_quantity=total_quantity)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/pay')


@app.route('/index')
def index2():
    return render_template('base/base.html')

@app.route('/api/pay', methods=['post'])
def pay():
    data = request.json
    id_user = data.get('id_user')
    id_cart = data.get('cart')
    bill = Bill(idUser = id_user, address_delivery='1', phone_delivery='1', name_delivery='1')
    db.session.add(bill)
    cart = utils.get_item_by_id_cart(id_cart)
    for p in cart:
        bill_detail = BillDetail(Bill=bill, idBook=p.idBook, price=p.discount, quantity=p.quantity)
        db.session.add(bill_detail)
        db.session.delete(p)

    db.session.commit()
    return jsonify({
        'message':'success'
    })


@app.route('/search', methods=['GET', 'POST'])
def search():
    # if request.method == "POST":
    #     name=request.form.get('Search')
    #     found_book=next(name for name in Book if Book.name==name)
    #     cursor.executemany('''select * from Book where name = %s''', )
    #     return render_template("search.html", records=cursor.fetchall())
     return render_template('search.html')

@app.route('/book')
def book():
    products = Book.query.all()
    # if request.method == "POST":
    #     name=request.form.get('Search')
    #     found_book=next(name for name in Book if Book.name==name)
    #     cursor.executemany('''select * from Book where name = %s''', )
    #     return render_template("search.html", records=cursor.fetchall())
    return render_template('listbook.html', products=products,list_book_category=utils.get_book_category())

@app.route('/single/<int:id_book>', methods=['GET'])
def load_detail_book_by_id(id_book):
    book=utils.get_book_by_id(id_book)
    return render_template('single.html', book = book, list_image = utils.get_image_by_id_book(id_book))



if __name__ == "__main__":
    app.run(port=8999, debug=True)


# dang nhap admin, pass 123
# insert mysql admin, pass 202cb962ac59075b964b07152d234b70