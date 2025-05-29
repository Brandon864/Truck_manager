from flask import Flask, render_template, request, redirect, url_for, flash
from database import Session, Truck, Driver, Delivery, User
from sqlalchemy import and_, or_
from flask_mail import Mail, Message
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'  

# Configure Flask-Mail (replace with your email settings)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

session = Session()

# User class for Flask-Login
class UserModel(User, UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = session.query(User).get(int(user_id))
    if user:
        user_model = UserModel()
        user_model.id = user.id
        user_model.username = user.username
        user_model.password = user.password
        return user_model
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            if session.query(User).filter_by(username=username).first():
                flash('Error: Username already exists.', 'error')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(username=username, password=hashed_password)
            session.add(user)
            session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            session.rollback()
            flash('Error: Could not register user.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = session.query(User).filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                user_model = UserModel()
                user_model.id = user.id
                user_model.username = user.username
                user_model.password = user.password
                login_user(user_model)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error: Invalid username or password.', 'error')
        except:
            flash('Error: Could not log in.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    truck_count = session.query(Truck).count()
    driver_count = session.query(Driver).count()
    active_delivery_count = session.query(Delivery).filter(Delivery.status.in_(['Goods Picked', 'In Transit'])).count()
    recent_deliveries = session.query(Delivery).order_by(Delivery.id.desc()).limit(5).all()
    scheduled_deliveries = session.query(Delivery).filter(
        and_(Delivery.start_datetime >= datetime.now(), Delivery.status.in_(['Pending', 'Goods Picked', 'In Transit']))
    ).order_by(Delivery.start_datetime).limit(5).all()
    return render_template('index.html', truck_count=truck_count, driver_count=driver_count, 
                         active_delivery_count=active_delivery_count, recent_deliveries=recent_deliveries,
                         scheduled_deliveries=scheduled_deliveries)

@app.route('/add_truck', methods=['GET', 'POST'])
@login_required
def add_truck():
    if request.method == 'POST':
        try:
            truck = Truck(
                truck_id=request.form['truck_id'],
                type=request.form['type'],
                capacity=float(request.form['capacity']),
                status='Available'
            )
            session.add(truck)
            session.commit()
            print(f"Added truck: {truck.truck_id}, Type: {truck.type}, Capacity: {truck.capacity}")
            flash('Truck added successfully!', 'success')
            return redirect(url_for('trucks'))
        except:
            session.rollback()
            flash('Error: Truck ID must be unique.', 'error')
    return render_template('add_truck.html')

@app.route('/add_driver', methods=['GET', 'POST'])
@login_required
def add_driver():
    trucks = session.query(Truck).all()
    if request.method == 'POST':
        try:
            driver = Driver(
                name=request.form['name'],
                phone=request.form['phone'],
                license_number=request.form['license_number'],
                email=request.form['email'],
                truck_id=int(request.form['truck_id']) if request.form['truck_id'] else None
            )
            session.add(driver)
            session.commit()
            flash('Driver added successfully!', 'success')
            return redirect(url_for('drivers'))
        except:
            session.rollback()
            flash('Error: Could not add driver.', 'error')
    return render_template('add_driver.html', trucks=trucks)

@app.route('/add_delivery', methods=['GET', 'POST'])
@login_required
def add_delivery():
    trucks = session.query(Truck).filter_by(status='Available').all()
    active_deliveries = session.query(Delivery).filter(Delivery.status.in_(['Goods Picked', 'In Transit'])).all()
    active_driver_ids = [delivery.driver_id for delivery in active_deliveries]
    drivers = session.query(Driver).filter(~Driver.id.in_(active_driver_ids)).all()
    
    if request.method == 'POST':
        try:
            start_datetime_str = request.form['start_datetime']
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M') if start_datetime_str else None
            delivery = Delivery(
                pickup_location=request.form['pickup_location'],
                dropoff_location=request.form['dropoff_location'],
                truck_id=int(request.form['truck_id']),
                driver_id=int(request.form['driver_id']),
                status='Pending',
                start_datetime=start_datetime
            )
            truck = session.query(Truck).get(int(request.form['truck_id']))
            driver = session.query(Driver).get(int(request.form['driver_id']))
            truck.status = 'In Use'
            driver.truck_id = truck.id
            session.add(delivery)
            session.commit()

            flash('Delivery added successfully!', 'success')
            return redirect(url_for('deliveries'))
        except Exception as e:
            session.rollback()
            flash(f'Error: Could not add delivery. {str(e)}', 'error')
    return render_template('add_delivery.html', trucks=trucks, drivers=drivers)

@app.route('/trucks')
@login_required
def trucks():
    trucks = session.query(Truck).all()
    return render_template('trucks.html', trucks=trucks)

@app.route('/drivers')
@login_required
def drivers():
    drivers = session.query(Driver).all()
    return render_template('drivers.html', drivers=drivers)

@app.route('/deliveries')
@login_required
def deliveries():
    deliveries = session.query(Delivery).all()
    return render_template('deliveries.html', deliveries=deliveries)

@app.route('/mark_goods_picked/<int:delivery_id>')
@login_required
def mark_goods_picked(delivery_id):
    try:
        delivery = session.query(Delivery).get(delivery_id)
        if delivery:
            if delivery.status != 'Pending':
                flash('Error: Delivery must be in Pending status to mark as Goods Picked.', 'error')
            else:
                delivery.status = 'Goods Picked'
                session.commit()
                flash('Delivery marked as Goods Picked!', 'success')
        else:
            flash('Error: Delivery not found.', 'error')
        return redirect(url_for('deliveries'))
    except:
        session.rollback()
        flash('Error: Could not mark as Goods Picked.', 'error')
        return redirect(url_for('deliveries'))

@app.route('/mark_in_transit/<int:delivery_id>')
@login_required
def mark_in_transit(delivery_id):
    try:
        delivery = session.query(Delivery).get(delivery_id)
        if delivery:
            if delivery.status != 'Goods Picked':
                flash('Error: Delivery must be in Goods Picked status to mark as In Transit.', 'error')
            else:
                delivery.status = 'In Transit'
                session.commit()
                flash('Delivery marked as In Transit!', 'success')
        else:
            flash('Error: Delivery not found.', 'error')
        return redirect(url_for('deliveries'))
    except:
        session.rollback()
        flash('Error: Could not mark as In Transit.', 'error')
        return redirect(url_for('deliveries'))

@app.route('/complete_delivery/<int:delivery_id>')
@login_required
def complete_delivery(delivery_id):
    try:
        delivery = session.query(Delivery).get(delivery_id)
        if delivery:
            if delivery.status != 'In Transit':
                flash('Error: Delivery must be In Transit to mark as Delivered.', 'error')
            else:
                delivery.status = 'Delivered'
                truck = delivery.truck
                truck.status = 'Available'
                driver = delivery.driver
                driver.truck_id = None
                session.commit()
                flash('Delivery marked as Delivered!', 'success')
        else:
            flash('Error: Delivery not found.', 'error')
        return redirect(url_for('deliveries'))
    except:
        session.rollback()
        flash('Error: Could not mark as Delivered.', 'error')
        return redirect(url_for('deliveries'))

if __name__ == '__main__':
    app.run(debug=True)