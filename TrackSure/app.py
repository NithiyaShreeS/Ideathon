from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'tracksure_ideathon_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracksure.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    points = db.Column(db.Integer, default=120)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    service = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Assigned")
    eta = db.Column(db.String(20), default="20 mins")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(phone=data['phone']).first()
    if not user:
        user = User(name=data.get('name', 'User'), phone=data['phone'])
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return jsonify({"success": True, "name": user.name, "points": user.points})

@app.route('/api/book', methods=['POST'])
def book():
    user = User.query.get(session.get('user_id'))
    if not user: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    new_order = Order(user_id=user.id, service=data['service'])
    user.points += 30 
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"success": True, "points": user.points})

@app.route('/api/data')
def get_data():
    user = User.query.get(session.get('user_id'))
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    # AI Prediction Logic based on time
    hr = datetime.now().hour
    is_rainy = hr > 17 or hr < 8
    ai_msg = "High Delay Risk Today!" if is_rainy else "Smooth Delivery Predicted"
    ai_desc = "Delivery might be late due to heavy rain and traffic." if is_rainy else "Traffic is clear. Expect on-time service."
    
    return jsonify({
        "points": user.points,
        "ai_title": ai_msg,
        "ai_desc": ai_desc,
        "orders": [{"service": o.service, "status": o.status, "eta": o.eta} for o in orders]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)