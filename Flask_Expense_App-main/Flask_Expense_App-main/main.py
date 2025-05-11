from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymysql
from support import (
    connect_db, close_db, execute_query, generate_df, top_tiles, 
    generate_Graph, makePieChart, get_monthly_data, meraScatter, 
    meraHeatmap, month_bar, meraSunburst
)
import pandas as pd
from datetime import datetime
import json
import plotly.express as px

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM user_login WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    close_db(conn, cursor)
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn, cursor = connect_db()
        try:
            cursor.execute("INSERT INTO user_login (username, email, password) VALUES (%s, %s, %s)",
                         (username, email, password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        except pymysql.Error as e:
            flash('Email already exists!', 'error')
        finally:
            close_db(conn, cursor)
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM user_login WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    close_db(conn, cursor)
    
    if user:
        user_obj = User(user[0], user[1], user[2])
        login_user(user_obj)
        return redirect(url_for('home'))
    flash('Invalid email or password!', 'error')
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM user_expenses WHERE user_id = %s ORDER BY pdate DESC LIMIT 5", (current_user.id,))
    table_data = cursor.fetchall()
    cursor.execute("SELECT * FROM user_expenses WHERE user_id = %s", (current_user.id,))
    expenses = cursor.fetchall()
    close_db(conn, cursor)
    
    if expenses:
        df = pd.DataFrame(expenses, columns=['id', 'user_id', 'Date', 'Expense', 'Amount', 'Note'])
        df = generate_df(df)
        earning, spend, invest, saving = top_tiles(df)
        bar, pie, line, stack_bar = generate_Graph(df)
        
        # Generate pie charts for each expense type
        pie1 = makePieChart(df, expense='Earning', names='Note', values='Amount', hole=0.5)
        pie2 = makePieChart(df, expense='Spend', names='Note', values='Amount', hole=0.5)
        pie3 = makePieChart(df, expense='Investment', names='Note', values='Amount', hole=0.5)
        pie4 = makePieChart(df, expense='Saving', names='Note', values='Amount', hole=0.5)
        pie5 = makePieChart(df, expense='Earning', names='Note', values='Amount', hole=0.5, color_discrete_sequence=px.colors.sequential.Plasma)
        pie6 = makePieChart(df, expense='Spend', names='Note', values='Amount', hole=0.5, color_discrete_sequence=px.colors.sequential.Plasma)
        
        monthly_data = get_monthly_data(df)
        card_data = [
            {'head': 'Total Earnings', 'main': f'₹{earning}', 'msg': 'This month'},
            {'head': 'Total Spends', 'main': f'₹{spend}', 'msg': 'This month'},
            {'head': 'Total Investments', 'main': f'₹{invest}', 'msg': 'This month'},
            {'head': 'Total Savings', 'main': f'₹{saving}', 'msg': 'This month'}
        ]
        goals = []  # Add goals if needed
        return render_template('home.html', 
                             user_name=current_user.username,
                             earning=earning,
                             spend=spend,
                             invest=invest,
                             saving=saving,
                             bar=bar,
                             pie=pie,
                             line=line,
                             stack_bar=stack_bar,
                             pie1=pie1,
                             pie2=pie2,
                             pie3=pie3,
                             pie4=pie4,
                             pie5=pie5,
                             pie6=pie6,
                             table_data=table_data, 
                             df_size=len(expenses),
                             monthly_data=monthly_data,
                             card_data=card_data,
                             goals=goals)
    
    # If no expenses, return empty graphs
    empty_graph = json.dumps({})
    return render_template('home.html', 
                         user_name=current_user.username,
                         earning=0,
                         spend=0,
                         invest=0,
                         saving=0,
                         bar=empty_graph,
                         pie=empty_graph,
                         line=empty_graph,
                         stack_bar=empty_graph,
                         pie1=empty_graph,
                         pie2=empty_graph,
                         pie3=empty_graph,
                         pie4=empty_graph,
                         pie5=empty_graph,
                         pie6=empty_graph,
                         table_data=[], 
                         df_size=0,
                         monthly_data=[],
                         card_data=[],
                         goals=[])

@app.route('/home/add_expense', methods=['POST'])
@login_required
def add_expense():
    try:
        date = request.form['e_date']
        expense_type = request.form['e_type']
        amount = request.form['amount']
        note = request.form['note']
        
        conn, cursor = connect_db()
        cursor.execute("INSERT INTO user_expenses (user_id, pdate, expense, amount, pdescription) VALUES (%s, %s, %s, %s, %s)",
                      (current_user.id, date, expense_type, amount, note))
        conn.commit()
        close_db(conn, cursor)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('home'))
    except KeyError as e:
        flash(f'Missing required field: {str(e)}', 'error')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error adding expense: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form['email']
    password = request.form['password']
    
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM user_login WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    close_db(conn, cursor)
    
    if user:
        user_obj = User(user[0], user[1], user[2])
        login_user(user_obj)
        return redirect(url_for('home'))
    flash('Invalid email or password!', 'error')
    return redirect(url_for('index'))

@app.route('/analysis')
@login_required
def analysis():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM user_expenses WHERE user_id = %s", (current_user.id,))
    expenses = cursor.fetchall()
    close_db(conn, cursor)
    
    if expenses:
        df = pd.DataFrame(expenses, columns=['id', 'user_id', 'Date', 'Expense', 'Amount', 'Note'])
        df = generate_df(df)
        
        # Generate all required graphs
        bar, pie, line, stack_bar = generate_Graph(df)
        
        # Generate additional graphs
        scatter = meraScatter(df, x='Date', y='Amount', color='Expense', size='Amount', 
                            title='Expense Distribution Over Time')
        heat = meraHeatmap(df, x='Month_name', y='Expense', title='Monthly Expense Heatmap')
        monthly_bar = month_bar(df)
        sun = meraSunburst(df)
        
        return render_template('analysis.html',
                             user_name=current_user.username,
                             bar=bar,
                             pie=pie,
                             line=line,
                             scatter=scatter,
                             heat=heat,
                             month_bar=monthly_bar,
                             sun=sun)
    
    # If no expenses, return empty graphs
    empty_graph = json.dumps({})
    return render_template('analysis.html',
                         user_name=current_user.username,
                         bar=empty_graph,
                         pie=empty_graph,
                         line=empty_graph,
                         scatter=empty_graph,
                         heat=empty_graph,
                         month_bar=empty_graph,
                         sun=empty_graph)

@app.route('/updateprofile', methods=['POST'])
@login_required
def updateprofile():
    name = request.form['name']
    email = request.form['email']
    conn, cursor = connect_db()
    cursor.execute("UPDATE user_login SET username = %s, email = %s WHERE user_id = %s", (name, email, current_user.id))
    conn.commit()
    close_db(conn, cursor)
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    conn, cursor = connect_db()
    cursor.execute("SELECT username, email FROM user_login WHERE user_id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    close_db(conn, cursor)
    return render_template('profile.html', user_name=user_data[0], email=user_data[1])

if __name__ == '__main__':
    app.run(debug=True)
