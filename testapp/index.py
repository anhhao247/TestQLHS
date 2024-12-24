from flask.cli import routes_command

from testapp import app, dao, login
from flask import request, render_template, session, redirect, url_for, flash, jsonify, abort
from testapp.admin import *
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required
from testapp.models import UserRole, Semester, Student
from functools import wraps
from datetime import datetime

def admin_or_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and current_user.user_role == UserRole.ADMIN:
                # ADMIN được phép truy cập tất cả
                return f(*args, **kwargs)
            elif current_user.is_authenticated and current_user.user_role == role:
                # Kiểm tra nếu đúng vai trò yêu cầu
                return f(*args, **kwargs)
            else:
                # Từ chối truy cập
                abort(403)
        return decorated_function
    return decorator

# def teacher_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated or current_user.user_role != UserRole.TEACHER:
#             abort(403)  # Forbidden
#         return f(*args, **kwargs)
#
#     return decorated_function
#
# def staff_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated or current_user.user_role != UserRole.STAFF:
#             abort(403)  # Forbidden
#         return f(*args, **kwargs)
#
#     return decorated_function


@app.context_processor
def inject_user_role():
    return dict(UserRole=UserRole)



@app.route('/')
def index():
    return render_template('index.html')

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id)

@app.route('/login', methods=['GET', 'POST'])
def user_signin():
    err_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = dao.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            nextr = request.args.get('next')
            return redirect(nextr if nextr else '/')
        else:
            err_msg = 'Invalid username or password'
    return render_template('login.html', err_msg=err_msg)

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = dao.check_login(username=username, password=password, role=UserRole.ADMIN)
        if user:
            login_user(user=user)
    return redirect('/admin')

@app.route('/user-logout')
def logout_process():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/nhap-diem')
@login_required
@admin_or_required(role=UserRole.TEACHER)
def nhapdiem():
    lops = Lop.query.all()
    hk = Semester.query.all()
    mh = Subject.query.all()
    namhoc = SchoolYear.query.all()
    return render_template('nhapdiem.html', lops=lops, hk=hk, mh=mh, namhoc=namhoc)


# Route để thêm học sinh mới
@app.route('/tiep-nhan-hoc-sinh', methods=['GET', 'POST'])
@login_required
@admin_or_required(role=UserRole.TEACHER)
def tiep_nhan_hoc_sinh():
    if request.method == 'POST':
        # Lấy thông tin từ form
        ho = request.form['ho']
        ten = request.form['ten']
        sex = request.form['sex']
        dob = datetime.strptime(request.form['DoB'], '%Y-%m-%d')  # Chuyển đổi từ string sang datetime
        address = request.form['address']
        sdt = request.form['sdt']
        email = request.form['email']

        # Tính tuổi của học sinh
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # Tính tuổi

        # Kiểm tra độ tuổi học sinh (từ 15 đến 20 tuổi)
        if age < 15 or age > 20:
            flash('Học sinh phải có độ tuổi từ 15 đến 20 tuổi.', 'error')
            return redirect(url_for('tiep_nhan_hoc_sinh'))  # Quay lại trang nhập học sinh

        # Tạo đối tượng học sinh mới
        student = Student(ho=ho, ten=ten, sex=sex, DoB=dob, address=address, sdt=sdt, email=email)

        # Thêm học sinh vào cơ sở dữ liệu
        db.session.add(student)
        db.session.commit()

        # Chuyển hướng về danh sách học sinh hoặc thông báo thành công
        # return redirect(url_for('danh_sach_hoc_sinh'))
    students = Student.query.all()
    return render_template('tiep_nhan_hoc_sinh.html', students=students)


@app.route('/danh-sach-lop')
@login_required
@admin_or_required(role=UserRole.STAFF)
def dslop():
    return render_template('danhsachlop.html')


if __name__ == '__main__':
    app.run(debug=True)