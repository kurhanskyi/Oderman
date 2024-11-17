from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzeria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()
    if not Pizza.query.first():
        initial_pizzas = [
            Pizza(name="Маргарита", ingredients="Томатний соус, моцарела, базилік", price=120),
            Pizza(name="Пепероні", ingredients="Томатний соус, моцарела, пепероні", price=140),
            Pizza(name="Гавайська", ingredients="Томатний соус, моцарела, шинка, ананаси", price=150),
            Pizza(name="Чотири сири", ingredients="Вершковий соус, моцарела, пармезан, горгонзола, чедер", price=160)
        ]
        db.session.add_all(initial_pizzas)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/menu')
def menu():
    sort = request.args.get('sort', 'name')
    reverse = request.args.get('reverse', 'false') == 'true'

    if sort == 'price':
        pizzas = Pizza.query.order_by(Pizza.price.desc() if reverse else Pizza.price)
    else:
        pizzas = Pizza.query.order_by(Pizza.name.desc() if reverse else Pizza.name)

    return render_template('menu.html', pizzas=pizzas, current_sort=sort, reverse=reverse)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        price = int(request.form['price'])

        new_pizza = Pizza(name=name, ingredients=ingredients, price=price)
        db.session.add(new_pizza)
        db.session.commit()
        flash('Піца успішно додана!')
        return redirect(url_for('admin'))

    pizzas = Pizza.query.all()
    return render_template('admin.html', pizzas=pizzas)


if __name__ == '__main__':
    app.run(debug=True)