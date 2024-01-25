from datetime import datetime as dt, timedelta
import datetime  
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'


db = SQLAlchemy(app)

# creating table called books

class Book(db.Model):
    __tablename__ = 'books'

    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Author = db.Column(db.String(50), nullable=False)
    YearPublished = db.Column(db.Integer, nullable=False)  
    Type = db.Column(db.Integer, nullable=False)

    def __init__(self ,Name ,Author ,YearPublished ,Type):
        self.Name=Name
        self.Author=Author
        self.YearPublished=YearPublished
        self.Type=Type
    
# creating table called customers

class Customers(db.Model):
    __tablename__ = 'customers'

    Id = db.Column(db.Integer, primary_key=True) 
    Name = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(50), nullable=False)
    Age = db.Column(db.String(5), nullable=False)

    def __init__(self ,Name ,City ,Age ):
        self.Name=Name
        self.City=City
        self.Age=Age

# creating table called users

class Users(db.Model):
    __tablename__ = 'users'

    Id = db.Column(db.Integer, primary_key=True) 
    Name = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(50), nullable=False)

 
    def __init__(self ,Name ,Password ):
        self.Name=Name
        self.Password=Password

# creating table called loans

class Loans(db.Model):
    __tablename__ = 'loans'

    LoanId = db.Column(db.Integer, primary_key=True)
    CustID = db.Column(db.Integer, db.ForeignKey('customers.Id'), nullable=False)
    BookID = db.Column(db.Integer, db.ForeignKey('books.Id'), nullable=False)
    Loandate = db.Column(db.String(50), nullable=False)
    Returndate = db.Column(db.String(50), nullable=False)

    def __init__(self, CustID, BookID, Loandate, Returndate):
        self.CustID = CustID
        self.BookID = BookID
        self.Loandate = Loandate
        self.Returndate = Returndate

  
        
#------------------------- #routes-------------------------------
@app.route('/books', methods=['GET'])
def display_books():
    try:
        books = Book.query.all()
        book_list = []

        for book in books:
            book_info = {
                'Id': book.Id,
                'Name': book.Name,
                'Author': book.Author,
                'YearPublished': book.YearPublished,
                'Type': book.Type
            }
            book_list.append(book_info)

        return jsonify({'books': book_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/customers', methods=['GET'])
def display_customers():
    try:
        customers = Customers.query.all()
        customer_list = []

        for customer in customers:
            customer_info = {
                'Id': customer.Id,
                'Name': customer.Name,
                'City': customer.City,
                'Age': customer.Age
            }
            customer_list.append(customer_info)

        return jsonify({'customers': customer_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/loans', methods=['GET'])
def display_loans():
    try:
        loans = Loans.query.all()
        loan_list = []

        for loan in loans:
            loan_info = {
                'LoanId': loan.LoanId,
                'CustID': loan.CustID,
                'BookID': loan.BookID,
                'Loandate': loan.Loandate,
                'Returndate': loan.Returndate
            }
            loan_list.append(loan_info)

        return jsonify({'loans': loan_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/loans/late', methods=['GET'])
def display_late_loans():
    try:
        current_date = dt.now()
        late_loans = Loans.query.filter(Loans.Returndate < current_date).all()

        late_loans_list = []

        for loan in late_loans:
            loan_info = {
                'LoanId': loan.LoanId,
                'CustID': loan.CustID,
                'BookID': loan.BookID,
                'Loandate': loan.Loandate,
                'Returndate': loan.Returndate
            }
            late_loans_list.append(loan_info)

        return jsonify({'past_due_loans': late_loans_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/users/new', methods=['POST'])
def create_users():
    data = request.get_json()

    new_user = Users(
        Name=data["name"],
    )
   
    exist = Users.query.filter_by(Name=data["name"]).first()
    if exist:
       return jsonify({'message': 'user exists'}), 201
 
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'user created successfully', 'user': new_user.Name, 'Id': new_user.Id}), 201        
  
@app.route('/customers/new', methods=['POST'])
def create_customers():
    data = request.get_json()

    new_customer = Customers(
        Name=data["name"],
        City=data["city"],
        Age=data["age"],
    )
   
    exist = Customers.query.filter_by(Name=data["name"],Age=data["age"]).first()
    if exist:
       return jsonify({'message': 'customer exists'}), 201
 
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'customer created successfully', 'customer': new_customer.Name, 'Id': new_customer.Id}), 201        
    

@app.route('/books/new', methods=['POST'])
def create_book():
    data = request.get_json()

    exist = Book.query.filter_by(Name=data["name"],Author=data["author"]).first()
    if exist:
       return jsonify({'message': 'book exists'}), 201
        

    new_book = Book(
        Name=data["name"],
        Author=data["author"],
        YearPublished=data["year"],
        Type=data["type"],
    )
   
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book created successfully', 'book': new_book.Name}), 201


@app.route('/books/delete', methods=['DELETE'])
def delete_books():
    try:
        data = request.get_json()

        # Check if the required keys are present in the JSON data
        if not data or "name" not in data or "author" not in data:
            return jsonify({'error': 'Missing required fields (name and author)'}), 400

        # Check if the book exists
        exist = Book.query.filter_by(Name=data["name"], Author=data["author"]).first()
        if not exist:
            return jsonify({'error': 'Book not found'}), 404

        # Delete the book
        db.session.delete(exist)
        db.session.commit()

        return jsonify({'message': 'Book deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/loans/new', methods=['POST'])
def create_loan():
    try:
        data = request.get_json()

        # Check if the required keys are present in the JSON data
        if not data or "cust_id" not in data or "book_id" not in data:
            return jsonify({'error': 'Missing required fields (cust_id, book_id)'}), 400

        # Check if the customer exists
        customer_exist = Customers.query.get(data["cust_id"])
        if not customer_exist:
            return jsonify({'error': 'Customer not found'}), 404

        # Check if the book exists
        book_exist = Book.query.get(data["book_id"])
        if not book_exist:
            return jsonify({'error': 'Book not found'}), 404
        
         # Check if the book has already loaned        
        book_loaned = Loans.query.filter_by(BookID=data["book_id"]).first()
        if book_loaned:
            return jsonify({'error': 'the book has already loaned'}), 404

        # Set default loan dates
        loan_date = dt.now()
        return_date = (dt.now() + timedelta(days=2))
        print(f"Current Date: {loan_date}")
        print(f"Date of Now +2 Days: {return_date}")

        # Adjust dates based on the book's type
        if book_exist.Type == 2:
            return_date = (dt.now() + timedelta(days=5))
        elif book_exist.Type == 3:
            return_date = (dt.now() + timedelta(days=10))

        # Create a new loan
        new_loan = Loans(
            CustID=data["cust_id"],
            BookID=data["book_id"],
            Loandate=loan_date,
            Returndate=return_date,
        )

        db.session.add(new_loan)
        db.session.commit()

        return jsonify({'message': 'Loan created successfully', 'loan_id': new_loan.LoanId}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/loans/delete', methods=['DELETE'])
def delete_loans():
    try:
        data = request.get_json()

        # Check if the required keys are present in the JSON data
        if not data:
           return jsonify({'error': 'Missing required fields (id)'}), 400

        # Check if the loan exists
        exist = Loans.query.filter_by(CustID=data["cust_id"],BookID=data["book_id"]).first()
        if not exist:
           return jsonify({'error': 'loan not found'}), 404

        print('Loan created successfully')
        # Delete the loan
        db.session.delete(exist)
        db.session.commit()

        return jsonify({'message': 'loan deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/books/search', methods=['GET'])
def search_books():
    try:
        data = request.get_json()

        book = Book.query.filter_by(Name=data["name"]).first()

        if not book:
            return jsonify({'massage': 'book is not exist'})


        return jsonify({'books': {
            'Id': book.Id,
            'Name': book.Name,
            'Author': book.Author,
            'YearPublished': book.YearPublished,
            'Type': book.Type
        }})


    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/customer/search', methods=['GET'])
def search_customer():
    try:
        data = request.get_json()
        customer = Customers.query.filter_by(Name=data["name"]).first()

        if not customer:
            return jsonify({'massage': 'customer is not exist'})


        return jsonify({'books': {
            'Name': customer.Name,
            'City': customer.City,
            'Age': customer.Age
        }})
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True)