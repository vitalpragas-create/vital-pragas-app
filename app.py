from datetime import date, datetime
from functools import wraps
import os

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func, or_
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'app.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vital-pragas-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80))
    unit = db.Column(db.String(20), default='UN')
    internal_code = db.Column(db.String(60))
    batch = db.Column(db.String(60))
    expiry_date = db.Column(db.Date)
    supplier = db.Column(db.String(120))
    quantity = db.Column(db.Float, default=0)
    minimum_stock = db.Column(db.Float, default=0)
    location = db.Column(db.String(120))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Ativo')

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(20))
    role = db.Column(db.String(80))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    admission_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Ativo')
    notes = db.Column(db.Text)

class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    movement_type = db.Column(db.String(30), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    signature_data = db.Column(db.Text)
    expected_return_date = db.Column(db.Date)
    return_date = db.Column(db.Date)

    product = db.relationship('Product')
    employee = db.relationship('Employee')

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(80))
    plate = db.Column(db.String(20))
    year = db.Column(db.String(10))
    purchase_date = db.Column(db.Date)
    purchase_place = db.Column(db.String(120))
    status = db.Column(db.String(20), default='Disponível')
    notes = db.Column(db.Text)

class EquipmentAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    expected_return_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    delivery_condition = db.Column(db.String(120))
    return_condition = db.Column(db.String(120))
    notes = db.Column(db.Text)
    signature_data = db.Column(db.Text)
    status = db.Column(db.String(20), default='Entregue')

    equipment = db.relationship('Equipment')
    employee = db.relationship('Employee')

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_type = db.Column(db.String(80), nullable=False)
    maintenance_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    provider = db.Column(db.String(120))
    location = db.Column(db.String(120))
    cost = db.Column(db.Float)
    next_maintenance_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    equipment = db.relationship('Equipment')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_date = db.Column(db.Date, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    system_quantity = db.Column(db.Float, nullable=False)
    physical_quantity = db.Column(db.Float, nullable=False)
    difference = db.Column(db.Float, nullable=False)
    responsible = db.Column(db.String(120))
    notes = db.Column(db.Text)

    product = db.relationship('Product')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Apenas administradores podem acessar esta área.', 'warning')
            return redirect(url_for('dashboard'))
        return view_func(*args, **kwargs)
    return wrapped


def parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date() if value else None


def seed_data():
    if not User.query.first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    if not Product.query.first():
        db.session.add_all([
            Product(name='Inseticida Ultra', category='Inseticida', brand='BioTech', unit='L', internal_code='INS001', batch='LT001', expiry_date=date(2026, 11, 10), supplier='Fornecedor A', quantity=25, minimum_stock=10, location='A1'),
            Product(name='Raticida Forte', category='Raticida', brand='SafeKill', unit='KG', internal_code='RAT002', batch='LT002', expiry_date=date(2026, 8, 15), supplier='Fornecedor B', quantity=8, minimum_stock=10, location='B2'),
        ])
        db.session.add_all([
            Employee(full_name='Carlos Silva', role='Técnico', phone='(66) 99999-0001', status='Ativo'),
            Employee(full_name='Marcos Souza', role='Operador', phone='(66) 99999-0002', status='Ativo'),
        ])
        db.session.add(Equipment(equipment_type='Moto', description='Honda CG 160', brand='Honda', model='CG 160', serial_number='MOTO-01', plate='ABC1D23', year='2024', purchase_place='Concessionária X', status='Disponível'))
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.minimum_stock).count()
    total_employees = Employee.query.count()
    equipment_in_use = Equipment.query.filter_by(status='Em uso').count()
    recent_movements = StockMovement.query.order_by(StockMovement.movement_date.desc()).limit(8).all()
    expiring_products = Product.query.filter(Product.expiry_date != None).order_by(Product.expiry_date.asc()).limit(5).all()
    upcoming_maintenance = Maintenance.query.filter(Maintenance.next_maintenance_date != None).order_by(Maintenance.next_maintenance_date.asc()).limit(5).all()
    return render_template('dashboard.html', total_products=total_products, low_stock=low_stock, total_employees=total_employees,
                           equipment_in_use=equipment_in_use, recent_movements=recent_movements, expiring_products=expiring_products,
                           upcoming_maintenance=upcoming_maintenance)

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            category=request.form.get('category'),
            brand=request.form.get('brand'),
            unit=request.form.get('unit'),
            internal_code=request.form.get('internal_code'),
            batch=request.form.get('batch'),
            expiry_date=parse_date(request.form.get('expiry_date')),
            supplier=request.form.get('supplier'),
            quantity=float(request.form.get('quantity') or 0),
            minimum_stock=float(request.form.get('minimum_stock') or 0),
            location=request.form.get('location'),
            notes=request.form.get('notes'),
            status=request.form.get('status') or 'Ativo',
        )
        db.session.add(product)
        db.session.commit()
        flash('Produto cadastrado com sucesso.', 'success')
        return redirect(url_for('products'))
    q = request.args.get('q', '')
    items = Product.query
    if q:
        like = f'%{q}%'
        items = items.filter(or_(Product.name.ilike(like), Product.category.ilike(like), Product.brand.ilike(like)))
    items = items.order_by(Product.name.asc()).all()
    return render_template('products.html', products=items, q=q)

@app.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():
    if request.method == 'POST':
        employee = Employee(
            full_name=request.form.get('full_name'),
            cpf=request.form.get('cpf'),
            role=request.form.get('role'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            admission_date=parse_date(request.form.get('admission_date')),
            status=request.form.get('status') or 'Ativo',
            notes=request.form.get('notes'),
        )
        db.session.add(employee)
        db.session.commit()
        flash('Funcionário cadastrado com sucesso.', 'success')
        return redirect(url_for('employees'))
    return render_template('employees.html', employees=Employee.query.order_by(Employee.full_name.asc()).all())

@app.route('/movements', methods=['GET', 'POST'])
@login_required
def movements():
    if request.method == 'POST':
        product = Product.query.get_or_404(int(request.form.get('product_id')))
        employee_id = request.form.get('employee_id')
        movement_type = request.form.get('movement_type')
        quantity = float(request.form.get('quantity') or 0)

        if movement_type == 'Saída' and product.quantity < quantity:
            flash('Quantidade insuficiente em estoque.', 'danger')
            return redirect(url_for('movements'))

        if movement_type in ['Saída', 'Perda', 'Avaria', 'Descarte']:
            product.quantity -= quantity
        else:
            product.quantity += quantity

        movement = StockMovement(
            movement_type=movement_type,
            product_id=product.id,
            employee_id=int(employee_id) if employee_id else None,
            quantity=quantity,
            reason=request.form.get('reason'),
            notes=request.form.get('notes'),
            signature_data=request.form.get('signature_data'),
            expected_return_date=parse_date(request.form.get('expected_return_date')),
            return_date=parse_date(request.form.get('return_date')),
        )
        db.session.add(movement)
        db.session.commit()
        flash('Movimentação registrada com sucesso.', 'success')
        return redirect(url_for('movements'))

    items = StockMovement.query.order_by(StockMovement.movement_date.desc()).all()
    return render_template('movements.html', movements=items, products=Product.query.order_by(Product.name.asc()).all(), employees=Employee.query.order_by(Employee.full_name.asc()).all())

@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if request.method == 'POST':
        product = Product.query.get_or_404(int(request.form.get('product_id')))
        physical_quantity = float(request.form.get('physical_quantity') or 0)
        difference = physical_quantity - product.quantity
        inventory_item = Inventory(
            inventory_date=parse_date(request.form.get('inventory_date')) or date.today(),
            product_id=product.id,
            system_quantity=product.quantity,
            physical_quantity=physical_quantity,
            difference=difference,
            responsible=request.form.get('responsible'),
            notes=request.form.get('notes'),
        )
        product.quantity = physical_quantity
        db.session.add(inventory_item)
        db.session.commit()
        flash('Inventário registrado e estoque ajustado.', 'success')
        return redirect(url_for('inventory'))
    items = Inventory.query.order_by(Inventory.inventory_date.desc()).all()
    return render_template('inventory.html', items=items, products=Product.query.order_by(Product.name.asc()).all())

@app.route('/equipment', methods=['GET', 'POST'])
@login_required
def equipment():
    if request.method == 'POST':
        item = Equipment(
            equipment_type=request.form.get('equipment_type'),
            description=request.form.get('description'),
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            serial_number=request.form.get('serial_number'),
            plate=request.form.get('plate'),
            year=request.form.get('year'),
            purchase_date=parse_date(request.form.get('purchase_date')),
            purchase_place=request.form.get('purchase_place'),
            status=request.form.get('status') or 'Disponível',
            notes=request.form.get('notes'),
        )
        db.session.add(item)
        db.session.commit()
        flash('Equipamento cadastrado com sucesso.', 'success')
        return redirect(url_for('equipment'))
    return render_template('equipment.html', equipment_items=Equipment.query.order_by(Equipment.description.asc()).all())

@app.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    if request.method == 'POST':
        equipment = Equipment.query.get_or_404(int(request.form.get('equipment_id')))
        assignment = EquipmentAssignment(
            equipment_id=equipment.id,
            employee_id=int(request.form.get('employee_id')),
            delivery_date=parse_date(request.form.get('delivery_date')) or date.today(),
            expected_return_date=parse_date(request.form.get('expected_return_date')),
            return_date=parse_date(request.form.get('return_date')),
            delivery_condition=request.form.get('delivery_condition'),
            return_condition=request.form.get('return_condition'),
            notes=request.form.get('notes'),
            signature_data=request.form.get('signature_data'),
            status=request.form.get('status') or 'Entregue',
        )
        equipment.status = 'Em uso' if assignment.status == 'Entregue' else equipment.status
        db.session.add(assignment)
        db.session.commit()
        flash('Entrega de equipamento registrada com sucesso.', 'success')
        return redirect(url_for('assignments'))
    items = EquipmentAssignment.query.order_by(EquipmentAssignment.delivery_date.desc()).all()
    return render_template('assignments.html', items=items, equipment_items=Equipment.query.order_by(Equipment.description.asc()).all(), employees=Employee.query.order_by(Employee.full_name.asc()).all())

@app.route('/maintenance', methods=['GET', 'POST'])
@login_required
def maintenance():
    if request.method == 'POST':
        item = Maintenance(
            equipment_id=int(request.form.get('equipment_id')),
            maintenance_type=request.form.get('maintenance_type'),
            maintenance_date=parse_date(request.form.get('maintenance_date')) or date.today(),
            description=request.form.get('description'),
            provider=request.form.get('provider'),
            location=request.form.get('location'),
            cost=float(request.form.get('cost') or 0),
            next_maintenance_date=parse_date(request.form.get('next_maintenance_date')),
            notes=request.form.get('notes'),
        )
        db.session.add(item)
        db.session.commit()
        flash('Manutenção registrada com sucesso.', 'success')
        return redirect(url_for('maintenance'))
    items = Maintenance.query.order_by(Maintenance.maintenance_date.desc()).all()
    return render_template('maintenance.html', items=items, equipment_items=Equipment.query.order_by(Equipment.description.asc()).all())

@app.route('/reports')
@login_required
def reports():
    products = Product.query.order_by(Product.name.asc()).all()
    movements = StockMovement.query.order_by(StockMovement.movement_date.desc()).all()
    assignments = EquipmentAssignment.query.order_by(EquipmentAssignment.delivery_date.desc()).all()
    maintenance_items = Maintenance.query.order_by(Maintenance.maintenance_date.desc()).all()
    return render_template('reports.html', products=products, movements=movements, assignments=assignments, maintenance_items=maintenance_items)

@app.route('/signature/<kind>/<int:item_id>')
@login_required
def signature(kind, item_id):
    record = None
    if kind == 'movement':
        record = StockMovement.query.get_or_404(item_id)
    elif kind == 'assignment':
        record = EquipmentAssignment.query.get_or_404(item_id)
    return render_template('signature.html', record=record, kind=kind)

if __name__ == '__main__':
    app.run(debug=True)
