from __init__ import app
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from admin_models import *
from __init__ import login
from models import User
from flask_login import login_user, logout_user
import hashlib
import utils


@app.route('/info')
def info():
    return render_template('info.html')


@app.route("/")
def index():
    return render_template('base/base.html',  list_book= utils.load_Book(), list_book_image=utils.load_book_image(), list_book_category=utils.get_book_category())

@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)


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
    quantity = data.get('quantity')

    id_cart, list_item = utils.list_item_of_user(1)

    flag = 0
    for item in list_item:
        if (str(item.idBook) == id_book):
            item.quantity += quantity
            flag = 1
            db.session.commit()
    if (flag == 0):
        newitem = CartItem(idCart=id_cart, idBook=id_book, quantity=quantity, price=price, discount=price)
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

@app.route('/single/<int:id_book>', methods=['GET'])
def load_detail_book_by_id(id_book):
    book=utils.get_book_by_id(id_book)
    return render_template('single.html', book = book, list_image = utils.get_image_by_id_book(id_book))

@app.route('/api/check_would_buy', methods=['POST'])
def check_would_buy():
    data = request.json
    id_cart_item = str(data.get('id'))
    check = data.get('checked')
    cart_item = utils.get_item_cart_by_id(id_cart_item)
    t=2
    if(check=='true'):
        t=1
        utils.get_item_cart_by_id(id_cart_item).would_buy = 1
    else:
        t=0
        utils.get_item_cart_by_id(id_cart_item).would_buy = 0
    db.session.commit()
    return jsonify({
        'message': t
    })


if __name__ == "__main__":
    app.run(port=8999, debug=True)


# dang nhap admin, pass 123
# insert mysql admin, pass 202cb962ac59075b964b07152d234b70