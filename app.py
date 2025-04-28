from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"


def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  
        password='puneetha@1204',  
        database='StockManagement1'
    )
    return connection


@app.route('/')
def index():
    return render_template('index.html')

#users
@app.route('/users')
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    city = request.form['city']
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Users (name, email, phone, city, created_at) VALUES (%s, %s, %s, %s, %s)',
                      (name, email, phone, city, created_at))
        conn.commit()
        flash('User added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users'))

@app.route('/edit_user/<int:user_id>')
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    city = request.form['city']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Users SET name = %s, email = %s, phone = %s, city = %s WHERE user_id = %s',
                      (name, email, phone, city, user_id))
        conn.commit()
        flash('User updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Users WHERE user_id = %s', (user_id,))
        conn.commit()
        flash('User deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users'))


#stocks
@app.route('/stocks')
def stocks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Stocks')
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stocks.html', stocks=stocks)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    symbol = request.form['symbol']
    company_name = request.form['company_name']
    sector = request.form['sector']
    current_price = request.form['current_price']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Stocks (symbol, company_name, sector, current_price) VALUES (%s, %s, %s, %s)',
                      (symbol, company_name, sector, current_price))
        conn.commit()
        flash('Stock added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('stocks'))

@app.route('/brokers')
def brokers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Brokers')
    brokers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('brokers.html', brokers=brokers)

@app.route('/add_broker', methods=['POST'])
def add_broker():
    name = request.form['name']
    commission_rate = request.form['commission_rate']
    contact_email = request.form['contact_email']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Brokers (name, commission_rate, contact_email) VALUES (%s, %s, %s)',
                      (name, commission_rate, contact_email))
        conn.commit()
        flash('Broker added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('brokers'))



#transactions
@app.route('/transactions')
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT t.*, u.name as user_name, s.symbol, b.name as broker_name 
        FROM Transactions t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Stocks s ON t.stock_id = s.stock_id
        LEFT JOIN Brokers b ON t.broker_id = b.broker_id
    ''')
    transactions = cursor.fetchall()

    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM Stocks')
    stocks = cursor.fetchall()
    cursor.execute('SELECT * FROM Brokers')
    brokers = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('transactions.html', transactions=transactions, users=users, stocks=stocks, brokers=brokers)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    user_id = request.form['user_id']
    stock_id = request.form['stock_id']
    broker_id = request.form['broker_id']
    transaction_type = request.form['transaction_type']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])
    transaction_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Transactions 
            (user_id, stock_id, broker_id, transaction_type, quantity, price, transaction_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, stock_id, broker_id, transaction_type, quantity, price, transaction_date))

       
        if transaction_type == 'BUY':
            cursor.execute('SELECT * FROM Portfolio_Holdings WHERE user_id = %s AND stock_id = %s',
                           (user_id, stock_id))
            holding = cursor.fetchone()

            if holding:
                cursor.execute('''
                    UPDATE Portfolio_Holdings 
                    SET quantity = quantity + %s 
                    WHERE user_id = %s AND stock_id = %s
                ''', (quantity, user_id, stock_id))
            else:
                cursor.execute('''
                    INSERT INTO Portfolio_Holdings 
                    (user_id, stock_id, quantity, purchase_date) 
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, stock_id, quantity, transaction_date))

        elif transaction_type == 'SELL':
            cursor.execute('''
                UPDATE Portfolio_Holdings 
                SET quantity = quantity - %s 
                WHERE user_id = %s AND stock_id = %s
            ''', (quantity, user_id, stock_id))

            cursor.execute('''
                DELETE FROM Portfolio_Holdings 
                WHERE user_id = %s AND stock_id = %s AND quantity <= 0
            ''', (user_id, stock_id))

        conn.commit()
        flash('Transaction recorded successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('transactions'))


#portfolio
@app.route('/portfolio')
def portfolio():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, u.name as user_name, s.symbol, s.company_name, s.current_price,
               (s.current_price * p.quantity) AS total_value
        FROM Portfolio_Holdings p
        JOIN Users u ON p.user_id = u.user_id
        JOIN Stocks s ON p.stock_id = s.stock_id
    ''')
    holdings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('portfolio.html', holdings=holdings)

#watchlist
@app.route('/watchlist')
def watchlist():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT w.*, u.name as user_name, s.symbol, s.company_name, s.current_price
        FROM Watchlist w
        JOIN Users u ON w.user_id = u.user_id
        JOIN Stocks s ON w.stock_id = s.stock_id
    ''')
    watchlist = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('watchlist.html', watchlist=watchlist)

@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    user_id = request.form['user_id']
    stock_id = request.form['stock_id']
    added_on = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Watchlist (user_id, stock_id, added_on) 
            VALUES (%s, %s, %s)
        ''', (user_id, stock_id, added_on))
        conn.commit()
        flash('Stock added to watchlist!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('watchlist'))


def log_action(action, performed_by):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Logs (action, performed_by, log_timestamp) VALUES (%s, %s, %s)',
                  (action, performed_by, timestamp))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
