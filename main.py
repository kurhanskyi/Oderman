from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  


def get_weather():
    api_key = "YOUR_API_KEY"
    city = "Kyiv"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        weather = {
            'temperature': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'recommendation': get_pizza_recommendation(round(data['main']['temp']))
        }
        return weather
    except:
        return {
            'temperature': 15,
            'description': "хмарно",
            'recommendation': "Спробуйте нашу Пепероні - ідеально для прохолодного дня!"
        }


def get_pizza_recommendation(temp):
    if temp < 10:
        return "Спробуйте нашу гарячу Діабло - зігріє в холодний день!"
    elif temp < 20:
        return "Рекомендуємо Пепероні - ідеальна для прохолодного дня!"
    else:
        return "Спробуйте нашу легку Маргариту - чудовий вибір для теплого дня!"


def init_db():
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()


    c.execute('DROP TABLE IF EXISTS menu')
    c.execute('''CREATE TABLE menu
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT NOT NULL,
                  price REAL NOT NULL)''')


    c.execute('DROP TABLE IF EXISTS orders')
    c.execute('''CREATE TABLE orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  address TEXT NOT NULL,
                  pizza_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL,
                  order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'new',
                  FOREIGN KEY (pizza_id) REFERENCES menu (id))''')


    initial_data = [
        ('Маргарита', 'Томатний соус, моцарела та базиліка', 199.00),
        ('Пепероні', 'Гостра🥵 пепероні, моцарела та томатний соус', 239.00),
        ('Діабло', 'Надгостра🔥 піца з салямі, перцем чилі, халапеньо та моцарелою', 259.00),
        ('Гавайська', 'Солодкувата піца з ананасами, куркою, кукурудзою та моцарелою', 229.00),
        ('4 сири', 'Розкішна піца з чотирма видами сиру: моцарела, пармезан, горгонзола, чеддер', 279.00),
        ('Карбонара', 'Вершкова піца з беконом, пармезаном, моцарелою та яєчним жовтком', 249.00),
    ]

    c.executemany('INSERT INTO menu (name, description, price) VALUES (?, ?, ?)', initial_data)
    conn.commit()
    conn.close()


@app.route('/')
def home():
    weather = get_weather()
    return render_template('home.html', weather=weather)


@app.route('/menu')
def menu():
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()
    c.execute('SELECT * FROM menu')
    items = c.fetchall()
    conn.close()
    return render_template('menu.html', items=items)


@app.route('/order/<int:pizza_id>', methods=['GET', 'POST'])
def order(pizza_id):
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone = request.form['phone']
        address = request.form['address']
        quantity = request.form['quantity']

        c.execute('''INSERT INTO orders 
                     (customer_name, phone, address, pizza_id, quantity)
                     VALUES (?, ?, ?, ?, ?)''',
                  (customer_name, phone, address, pizza_id, quantity))
        conn.commit()
        conn.close()

        flash('Ваше замовлення успішно оформлено! Ми зв\'яжемося з вами найближчим часом.', 'success')
        return redirect(url_for('menu'))

    c.execute('SELECT * FROM menu WHERE id = ?', (pizza_id,))
    pizza = c.fetchone()
    conn.close()

    return render_template('order.html', pizza=pizza)


@app.route('/orders')
def orders():
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()
    c.execute('''SELECT orders.*, menu.name, menu.price 
                 FROM orders 
                 JOIN menu ON orders.pizza_id = menu.id 
                 ORDER BY order_time DESC''')
    orders = c.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        conn = sqlite3.connect('instance/pizzeria.db')
        c = conn.cursor()
        c.execute('INSERT INTO menu (name, description, price) VALUES (?, ?, ?)',
                  (name, description, price))
        conn.commit()
        conn.close()
        return redirect(url_for('menu'))

    return render_template('admin.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        c.execute('UPDATE menu SET name = ?, description = ?, price = ? WHERE id = ?',
                  (name, description, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('menu'))

    c.execute('SELECT * FROM menu WHERE id = ?', (id,))
    item = c.fetchone()
    conn.close()
    return render_template('edit.html', item=item)


@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('instance/pizzeria.db')
    c = conn.cursor()
    c.execute('DELETE FROM menu WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('menu'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)