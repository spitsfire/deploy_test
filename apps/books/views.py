from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, UserManager, Book, BookManager
import bcrypt

def index(request):
    return render(request, 'books/index.html')

def register(request):
    errors = User.objects.register_validator(request.POST)

    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/')
    else:
        user = User.objects.create_user(request.POST)
        request.session['user_id'] = user.id
        request.session['greeting'] = user.first_name
        return redirect('/books')

def login(request):
    errors = User.objects.login_validator(request.POST)

    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/')
    else:
        user = User.objects.get(email=request.POST['login_email'])
        request.session['user_id'] = user.id
        request.session['greeting'] = user.first_name
        return redirect('/books')

def show_all(request):
    
    context = {
        'all_books': Book.objects.all(),
        'this_user': User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'books/show_all.html', context)

def create_book(request):
    errors = Book.objects.book_validator(request.POST)

    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/books')
    else:
        book = Book.objects.create_book(request.POST,request.session['user_id'])

        return redirect(f'/books/{book.id}')

def show_one(request, book_id):
    context = {
        'book': Book.objects.get(id=int(book_id)),
        'current_user': User.objects.get(id=int(request.session['user_id']))
    }
    return render(request, "books/show_one.html", context)

def update(request, book_id):
    book = Book.objects.get(id=int(book_id))
    book.description = request.POST['description']
    book.save()

    return redirect(f"/books/{book_id}")

def delete(request, book_id):
    book = Book.objects.get(id=int(book_id))
    book.delete()

    return redirect('/books')

def favorite(request, book_id):
    Book.objects.favorite(int(book_id), int(request.session['user_id']))

    return redirect(f'/books/{book_id}')

def unfavorite(request, book_id):
    Book.objects.unfavorite(int(book_id), int(request.session['user_id']))

    return redirect(f'/books/{book_id}')

def logout(request):
    request.session.flush()

    return redirect('/')
