import numpy as np


class Library:
    def __init__(self, how_many_books, signup_time, books):
        self.signup_time = signup_time
        self.books = books
        self.how_many_books = how_many_books
        self.is_signed_up = False

    def signup_step(self):
        if self.signup_time == 0:
            del self.signup_time
            self.is_signed_up = True
        else:
            self.signup_time -= 0
