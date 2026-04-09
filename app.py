from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# MySQL Configuration
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "medtracker")


# Database URL - use MySQL if environment variables are set, otherwise fall back to SQLite
DATABASE_URL = "mysql+mysqlconnector://medtracker:medtracker123@mysql:3306/medtracker"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@medtracker.com")

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

DOSE_UNITS = ["mg", "ml", "g", "mcg", "IU", "tablet(s)", "capsule(s)", "drop(s)"]
FREQ_UNITS = ["times/day", "times/week", "times/month", "hours"]

# ── Models ─────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    medicines     = db.relationship("Medicine", backref="user", lazy=True, cascade="all, delete-orphan")
    reminders     = db.relationship("Reminder", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, p):   self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)


class Patient(db.Model):
    __tablename__ = "patients"
    id              = db.Column(db.Integer, primary_key=True)
    first_name      = db.Column(db.String(100), nullable=False)
    last_name       = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=True)
    phone           = db.Column(db.String(20), nullable=True)
    date_of_birth   = db.Column(db.Date, nullable=True)
    gender          = db.Column(db.String(20), nullable=True)
    address         = db.Column(db.String(255), nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    allergies       = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"


class Medicine(db.Model):
    __tablename__      = "medicines"
    id                 = db.Column(db.Integer, primary_key=True)
    user_id            = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name               = db.Column(db.String(200), nullable=False)
    dosage_qty         = db.Column(db.Float,   nullable=True)
    dosage_unit        = db.Column(db.String(50),  nullable=True)
    dosage_freeform    = db.Column(db.String(200), nullable=True)
    frequency_qty      = db.Column(db.Integer, nullable=True)
    frequency_unit     = db.Column(db.String(50),  nullable=True)
    frequency_freeform = db.Column(db.String(200), nullable=True)
    notes              = db.Column(db.Text, nullable=True)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reminders          = db.relationship("Reminder",    backref="medicine", lazy=True, cascade="all, delete-orphan")
    history            = db.relationship("DoseHistory", backref="medicine", lazy=True, cascade="all, delete-orphan")

    @property
    def dosage_display(self):
        if self.dosage_freeform: return self.dosage_freeform
        if self.dosage_qty and self.dosage_unit:
            qty = int(self.dosage_qty) if self.dosage_qty == int(self.dosage_qty) else self.dosage_qty
            return f"{qty} {self.dosage_unit}"
        return "—"

    @property
    def frequency_display(self):
        if self.frequency_freeform: return self.frequency_freeform
        if self.frequency_qty and self.frequency_unit:
            return f"{self.frequency_qty} {self.frequency_unit}"
        return "—"


class Reminder(db.Model):
    __tablename__   = "reminders"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    medicine_id     = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    reminder_time   = db.Column(db.String(5), nullable=False)
    label           = db.Column(db.String(200), nullable=True)
    active          = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)


class DoseHistory(db.Model):
    __tablename__ = "dose_history"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    medicine_id   = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    taken_at      = db.Column(db.DateTime, default=datetime.utcnow)
    note          = db.Column(db.String(200), nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Auth routes ────────────────────────────────────────────────────────────────
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Welcome, {user.name}! Account created.", "success")
            return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        user     = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
        else:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    medicines  = Medicine.query.filter_by(user_id=current_user.id).order_by(Medicine.created_at.desc()).all()
    reminders  = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.reminder_time).all()
    today      = datetime.utcnow().date()
    today_doses = DoseHistory.query.filter(
        DoseHistory.user_id == current_user.id,
        db.func.date(DoseHistory.taken_at) == today
    ).count()
    return render_template("dashboard.html", medicines=medicines, reminders=reminders,
                           today_doses=today_doses, dose_units=DOSE_UNITS, freq_units=FREQ_UNITS)


# ── Medicine CRUD ──────────────────────────────────────────────────────────────
@app.route("/medicines/add", methods=["GET", "POST"])
@login_required
def add_medicine():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Medicine name is required.", "danger")
            return redirect(url_for("dashboard"))
        med = Medicine(user_id=current_user.id, name=name,
                       notes=request.form.get("notes", "").strip() or None)
        _apply_dose_freq(med, request.form)
        db.session.add(med)
        db.session.commit()
        flash(f"'{med.name}' added successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_medicine.html", dose_units=DOSE_UNITS, freq_units=FREQ_UNITS)


@app.route("/medicines/<int:med_id>/edit", methods=["GET", "POST"])
@login_required
def edit_medicine(med_id):
    med = Medicine.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Medicine name is required.", "danger")
            return redirect(url_for("edit_medicine", med_id=med_id))
        med.name = name
        med.notes = request.form.get("notes", "").strip() or None
        med.updated_at = datetime.utcnow()
        med.dosage_qty = med.dosage_unit = med.dosage_freeform = None
        med.frequency_qty = med.frequency_unit = med.frequency_freeform = None
        _apply_dose_freq(med, request.form)
        db.session.commit()
        flash(f"'{med.name}' updated successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("edit_medicine.html", med=med, dose_units=DOSE_UNITS, freq_units=FREQ_UNITS)


@app.route("/medicines/<int:med_id>/delete", methods=["POST"])
@login_required
def delete_medicine(med_id):
    med = Medicine.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    name = med.name
    db.session.delete(med)
    db.session.commit()
    flash(f"'{name}' deleted.", "info")
    return redirect(url_for("dashboard"))


@app.route("/medicines/<int:med_id>/log", methods=["POST"])
@login_required
def log_dose(med_id):
    med = Medicine.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    db.session.add(DoseHistory(user_id=current_user.id, medicine_id=med.id,
                               note=request.form.get("note", "").strip() or None))
    db.session.commit()
    flash(f"Dose of '{med.name}' logged!", "success")
    return redirect(url_for("dashboard"))


# ── History ────────────────────────────────────────────────────────────────────
@app.route("/history")
@login_required
def history():
    filter_med = request.args.get("medicine_id", "all")
    page       = request.args.get("page", 1, type=int)
    query      = DoseHistory.query.filter_by(user_id=current_user.id)
    if filter_med != "all":
        query = query.filter_by(medicine_id=int(filter_med))
    entries   = query.order_by(DoseHistory.taken_at.desc()).paginate(page=page, per_page=20)
    medicines = Medicine.query.filter_by(user_id=current_user.id).all()
    return render_template("history.html", entries=entries, medicines=medicines, filter_med=filter_med)


# ── Reminders ──────────────────────────────────────────────────────────────────
@app.route("/reminders/add", methods=["POST"])
@login_required
def add_reminder():
    med_id   = request.form.get("medicine_id")
    time_str = request.form.get("reminder_time", "").strip()
    label    = request.form.get("label", "").strip()
    if not med_id or not time_str:
        flash("Medicine and time are required.", "danger")
        return redirect(url_for("dashboard"))
    med = Medicine.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
    db.session.add(Reminder(user_id=current_user.id, medicine_id=med.id,
                            reminder_time=time_str, label=label or None))
    db.session.commit()
    flash(f"Reminder set for {med.name} at {time_str}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/reminders/<int:rem_id>/toggle", methods=["POST"])
@login_required
def toggle_reminder(rem_id):
    rem = Reminder.query.filter_by(id=rem_id, user_id=current_user.id).first_or_404()
    rem.active = not rem.active
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/reminders/<int:rem_id>/delete", methods=["POST"])
@login_required
def delete_reminder(rem_id):
    rem = Reminder.query.filter_by(id=rem_id, user_id=current_user.id).first_or_404()
    db.session.delete(rem)
    db.session.commit()
    flash("Reminder deleted.", "info")
    return redirect(url_for("dashboard"))


# ── Helpers ────────────────────────────────────────────────────────────────────
def _apply_dose_freq(med, form):
    if form.get("dose_mode") == "structured":
        med.dosage_qty  = float(form.get("dosage_qty") or 0) or None
        med.dosage_unit = form.get("dosage_unit", "").strip() or None
    else:
        med.dosage_freeform = form.get("dosage_freeform", "").strip() or None

    if form.get("freq_mode") == "structured":
        med.frequency_qty  = int(form.get("frequency_qty") or 0) or None
        med.frequency_unit = form.get("frequency_unit", "").strip() or None
    else:
        med.frequency_freeform = form.get("frequency_freeform", "").strip() or None


# ── Reminder email job ─────────────────────────────────────────────────────────
def send_reminders():
    with app.app_context():
        now          = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        for reminder in Reminder.query.filter_by(active=True, reminder_time=current_time).all():
            user = reminder.user
            med  = reminder.medicine
            if not user or not med:
                continue
            try:
                mail.send(Message(
                    subject=f"💊 Time to take {med.name}",
                    recipients=[user.email],
                    body=f"Hi {user.name},\n\nTime to take {med.name} — {med.dosage_display} ({med.frequency_display}).\n{reminder.label or ''}\n\n— MedTracker"
                ))
            except Exception as e:
                print(f"Email error: {e}")


# ── Start ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, trigger="interval", minutes=1, id="reminders")
    scheduler.start()

    app.run(debug=True)
