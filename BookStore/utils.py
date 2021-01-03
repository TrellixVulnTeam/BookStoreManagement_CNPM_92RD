# from BookStore import db
from models import Book, Image, BookCategory, User, Cart, CartItem, BillDetail, Bill
from __init__ import db
# from flask import session, sessions
# from BookStore.models import User

def load_Book():
    return Book.query.all()

def load_book_image():
    return Book.query.join(Image, Image.id_book == Book.id).add_column(Image.img)


def chek_login(username, password):
    print(username, password)
    return User.query.filter(User.username == username, User.password == password).first()

def get_user_by_id(user_id):
    return User.query.filter(User.id == user_id).all()


def cart_stats(id_user):
    count = 0
    price = 0

    id_cart , list_item = list_item_of_user(id_user)


    for i in list_item:
        count = count + i.quantity
        price = price + i.quantity * i.discount
    return count, price

def list_item_of_user(id_user):
    cart = Cart.query.filter(Cart.id_user == id_user).all()
    if(cart!=[]):
        id_cart = cart[0].id
    else:
        newcart = Cart(id_user=id_user)
        db.session.add(newcart)
        db.session.commit()
        id_cart = Cart.query.filter(Cart.id_user == id_user).first().id

    list_item = CartItem.query.filter(CartItem.idCart == id_cart).all()

    return id_cart, list_item

def list_item_of_user_name_book(id_user):
    cart = Cart.query.filter(Cart.id_user == id_user).all()
    if (cart != []):
        id_cart = cart[0].id
    else:
        newcart = Cart(id_user=id_user)
        db.session.add(newcart)
        db.session.commit()
        id_cart = Cart.query.filter(Cart.id_user == id_user).first().id

    list_item = CartItem.query.filter(CartItem.idCart == id_cart).join(Book, Book.id == CartItem.idBook).add_column(Book.name).all()

    return id_cart, list_item


def add_receipt(id_user):
    bill = Bill(id_user = id_user)
    db.session.add(bill)

    id_cart, list_item = list_item_of_user(id_user)

def get_item_by_id_cart(id_cart):
    return CartItem.query.filter(CartItem.idCart == id_cart).all()


def get_book_category():
    return BookCategory.query.all()


