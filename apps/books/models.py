from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import re, bcrypt

EMAIL_REGEX = re.compile('^[_a-z0-9-]+(.[_a-z0-9-]+)@[a-z0-9-]+(.[a-z0-9-]+)(.[a-z]{2,4})$')

class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        check = User.objects.filter(email=postData['email'])
        if len(postData['first_name']) < 2 or not postData['first_name'].isalpha():
            errors['first_name'] = "Please enter a valid first name and with only letters."
        if len(postData['last_name']) < 2 or not postData['last_name'].isalpha():
            errors['last_name'] = "Please enter a valid last name and with only letters."
        if len(postData['password']) < 8:
            errors['password'] = "Password cannot be less than 8 characters."
        elif postData['password'] != postData['confirm_password']:
            errors['password'] = "Passwords do not match."
        if len(postData['email']) < 1:
            errors['reg_email'] = "Email address cannot be blank."
        elif not re.match(EMAIL_REGEX, postData['email']):
            errors['reg_email'] = "Please enter a valid email address."
        elif check:
            errors['reg_email'] = "Email address is already registered."
        return errors
    
    def login_validator(self, postData):
        errors = {}
        check = User.objects.filter(email=postData['login_email'])
        if not check:
            errors['login_email'] = "Email has not been registered."
        else:
            if not bcrypt.checkpw(postData['login_password'].encode(), check[0].password.encode()):
                errors['login_email'] = "Email and password do not match."
        return errors

    def create_user(self, postData):
        user = User(
            first_name = postData['first_name'],
            last_name = postData['last_name'],
            email = postData['email'],
            password = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
        )
        user.save()
        return user


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = UserManager()

class BookManager(models.Manager):
    def book_validator(self, postData):
        errors = {}

        if len(postData['title']) < 1:
            errors['title'] = "Title must not be blank."
        if len(postData['description']) < 5:
            errors['description'] = "Description must at least 5 characters long."

        return errors
    
    def create_book(self, postData, user_id):
        user = User.objects.get(id=user_id)
        book = Book(
            title = postData['title'],
            description = postData['description'],
            creator = user
        )
        book.save()
        user.favorited_books.add(book)
        return book
    
    def favorite(self, book_id, user_id):
        user = User.objects.get(id=user_id)
        book = Book.objects.get(id=book_id)
        user.favorited_books.add(book)
    
    def unfavorite(self, book_id, user_id):
        user = User.objects.get(id=user_id)
        book = Book.objects.get(id=book_id)
        user.favorited_books.remove(book)


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    creator = models.ForeignKey(User, related_name="has_created_books")
    favorited_by = models.ManyToManyField(User, related_name="favorited_books")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = BookManager()