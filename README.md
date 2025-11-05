# Flask Shopping Cart Application

A full-featured shopping cart application built with Flask, featuring user authentication, product categories, shopping cart functionality, and payment processing.

## Features

- User Authentication (Register/Login)
- Product Categories
- Shopping Cart Management
- Product Search Functionality
- Secure Payment Processing
- Responsive Design with Bootstrap

## Project Structure

```
├── main.py              # Main application file
├── templates/           # HTML templates
│   ├── base.html       # Base template with common layout
│   ├── cart.html       # Shopping cart page
│   ├── categories.html # Product categories page
│   ├── home.html      # Homepage
│   ├── login.html     # User login page
│   ├── register.html  # User registration page
│   └── search.html    # Product search results page
└── instance/          # Instance-specific files (database)
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix or MacOS:
     ```
     source venv/bin/activate
     ```
4. Install required packages:
   ```
   pip install flask
   ```
5. Set up your SECRET_KEY & STRIPE_SECRET_KEY in .env file

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
   ```
   python main.py
   ```
3. Open your web browser and navigate to `http://localhost:5000`
4. Now to acess the Products - First You have to got to `http://localhost:5000/import-products` - After it shows Products added successfully - You can come back to homepage and explore

## Features in Detail

### User Authentication
- Secure user registration and login system
- Password hashing for security
- Session management

### Shopping Cart
- Add/remove items from cart
- Update quantities
- Calculate total price
- Persistent cart data

### Product Management
- Browse products by categories
- Search functionality
- Product details view

### Payment Processing
- Secure payment integration
- Order confirmation
- Payment success page

## Technologies Used

- Flask (Python web framework)
- SQLite (Database)
- HTML/CSS
- Bootstrap (Frontend framework)
- Jinja2 (Template engine)

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
