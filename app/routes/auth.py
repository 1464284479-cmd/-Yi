from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import re
from app.models import db, User, VerificationCode

auth_bp = Blueprint('auth', __name__)

# ==================== 工具函数 ====================

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def generate_captcha():
    """生成图形验证码（简化版，实际项目应使用 PIL 或其他库生成图片）"""
    import random
    import string
    captcha = ''.join(random.choices(string.digits, k=4))
    session['captcha'] = captcha
    return captcha

def verify_captcha(captcha_input):
    """验证图形验证码"""
    return session.get('captcha') == captcha_input

# ==================== 路由：F001 用户注册 ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册页面"""
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        contact_type = request.form.get('contact_type', 'phone')  # phone 或 email
        contact = phone if contact_type == 'phone' else email
        verification_code = request.form.get('verification_code', '').strip()
        
        errors = []
        
        # 1. 验证用户名
        if not username:
            errors.append('用户名不能为空')
        elif len(username) < 3 or len(username) > 20:
            errors.append('用户名长度应为3-20个字符')
        elif User.query.filter_by(username=username).first():
            errors.append('用户名已存在')
        
        # 2. 验证密码
        if not password:
            errors.append('密码不能为空')
        else:
            is_valid, msg = User.validate_password_strength(password)
            if not is_valid:
                errors.append(msg)
        
        if password != confirm_password:
            errors.append('两次密码输入不一致')
        
        # 3. 验证联系方式（手机号或邮箱）
        if not contact:
            errors.append('请填写手机号或邮箱')
        else:
            if contact_type == 'phone':
                if not validate_phone(phone):
                    errors.append('手机号格式不正确')
                elif User.query.filter_by(phone=phone).first():
                    errors.append('该手机号已注册')
            else:  # email
                try:
                    validate_email(email)
                    if User.query.filter_by(email=email).first():
                        errors.append('该邮箱已注册')
                except EmailNotValidError:
                    errors.append('邮箱格式不正确')
        
        # 4. 验证验证码
        if not verification_code:
            errors.append('请输入验证码')
        elif not VerificationCode.verify_code(contact, verification_code, 'register'):
            errors.append('验证码错误或已过期')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', 
                                   username=username, 
                                   phone=phone, 
                                   email=email,
                                   contact_type=contact_type)
        
        # 创建用户
        user = User(
            username=username,
            phone=phone if contact_type == 'phone' else None,
            email=email if contact_type == 'email' else None
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试', 'error')
    
    return render_template('register.html')

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    contact = request.form.get('contact', '').strip()
    code_type = request.form.get('code_type', 'register')
    
    if not contact:
        return jsonify({'success': False, 'message': '请填写手机号或邮箱'})
    
    # 验证联系方式格式
    is_phone = validate_phone(contact)
    is_email = False
    if not is_phone:
        try:
            validate_email(contact)
            is_email = True
        except EmailNotValidError:
            return jsonify({'success': False, 'message': '手机号或邮箱格式不正确'})
    
    # 检查是否已注册（注册时）
    if code_type == 'register':
        if is_phone and User.query.filter_by(phone=contact).first():
            return jsonify({'success': False, 'message': '该手机号已注册'})
        if is_email and User.query.filter_by(email=contact).first():
            return jsonify({'success': False, 'message': '该邮箱已注册'})
    elif code_type in ['login', 'reset_password']:
        if is_phone and not User.query.filter_by(phone=contact).first():
            return jsonify({'success': False, 'message': '该手机号未注册'})
        if is_email and not User.query.filter_by(email=contact).first():
            return jsonify({'success': False, 'message': '该邮箱未注册'})
    
    # 生成验证码
    code = VerificationCode.generate_code(contact, code_type)
    
    # TODO: 实际发送验证码（短信或邮件）
    # 这里仅用于演示，打印到控制台
    print(f"验证码已发送到 {contact}: {code}")
    
    return jsonify({
        'success': True, 
        'message': f'验证码已发送（演示：{code}）'
    })

# ==================== 路由：F002 用户登录 ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """普通用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        captcha = request.form.get('captcha', '').strip()
        
        errors = []
        
        if not username or not password:
            errors.append('请输入用户名和密码')
        
        if not captcha:
            errors.append('请输入验证码')
        elif not verify_captcha(captcha):
            errors.append('验证码错误')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('login.html', username=username)
        
        # 查找用户
        user = User.query.filter_by(username=username, is_admin=False).first()
        
        if not user:
            flash('用户名或密码错误', 'error')
            return render_template('login.html', username=username)
        
        # 检查是否锁定
        if user.is_locked():
            remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            flash(f'账号已锁定，请 {remaining_minutes} 分钟后再试', 'error')
            return render_template('login.html', username=username)
        
        # 验证密码
        if user.check_password(password):
            # 登录成功，重置失败次数
            user.reset_login_attempts()
            session['user_id'] = user.id
            session['username'] = user.username
            flash('登录成功！', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            # 密码错误
            user.increment_login_attempts(5, 10)
            remaining_attempts = 5 - user.login_attempts
            if remaining_attempts > 0:
                flash(f'密码错误，还有 {remaining_attempts} 次尝试机会', 'error')
            else:
                flash('密码错误次数过多，账号已被锁定10分钟', 'error')
            return render_template('login.html', username=username)
    
    return render_template('login.html')

# ==================== 路由：F003 管理员登录 ====================

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        errors = []
        
        if not username or not password:
            errors.append('请输入用户名和密码')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin_login.html', username=username)
        
        # 查找管理员
        admin = User.query.filter_by(username=username, is_admin=True).first()
        
        if not admin:
            flash('管理员账号不存在', 'error')
            return render_template('admin_login.html', username=username)
        
        # 检查是否锁定
        if admin.is_locked():
            remaining_minutes = int((admin.locked_until - datetime.utcnow()).total_seconds() / 60)
            flash(f'账号已锁定，请 {remaining_minutes} 分钟后再试', 'error')
            return render_template('admin_login.html', username=username)
        
        # 验证密码
        if admin.check_password(password):
            # 登录成功，重置失败次数
            admin.reset_login_attempts()
            session['user_id'] = admin.id
            session['username'] = admin.username
            session['is_admin'] = True
            flash('管理员登录成功！', 'success')
            return redirect(url_for('auth.admin_dashboard'))
        else:
            # 密码错误
            admin.increment_login_attempts(5, 10)
            remaining_attempts = 5 - admin.login_attempts
            if remaining_attempts > 0:
                flash(f'密码错误，还有 {remaining_attempts} 次尝试机会', 'error')
            else:
                flash('密码错误次数过多，账号已被锁定10分钟', 'error')
            return render_template('admin_login.html', username=username)
    
    return render_template('admin_login.html')

# ==================== 路由：F004 密码找回 ====================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """密码找回"""
    if request.method == 'POST':
        contact = request.form.get('contact', '').strip()
        verification_code = request.form.get('verification_code', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        errors = []
        
        # 验证联系方式
        is_phone = validate_phone(contact)
        is_email = False
        if not is_phone:
            try:
                validate_email(contact)
                is_email = True
            except EmailNotValidError:
                errors.append('手机号或邮箱格式不正确')
        
        # 查找用户
        user = None
        if not errors:
            if is_phone:
                user = User.query.filter_by(phone=contact, is_admin=False).first()
            elif is_email:
                user = User.query.filter_by(email=contact, is_admin=False).first()
            
            if not user:
                errors.append('该账号未注册或为管理员账号（管理员无法自主找回密码）')
        
        # 验证验证码
        if not verification_code:
            errors.append('请输入验证码')
        elif not VerificationCode.verify_code(contact, verification_code, 'reset_password'):
            errors.append('验证码错误或已过期')
        
        # 验证新密码
        if not new_password:
            errors.append('请输入新密码')
        else:
            is_valid, msg = User.validate_password_strength(new_password)
            if not is_valid:
                errors.append(msg)
        
        if new_password != confirm_password:
            errors.append('两次密码输入不一致')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('forgot_password.html', contact=contact)
        
        # 重置密码
        user.set_password(new_password)
        user.reset_login_attempts()  # 重置失败次数
        db.session.commit()
        
        flash('密码重置成功！请使用新密码登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

# ==================== 仪表盘和登出 ====================

@auth_bp.route('/dashboard')
def dashboard():
    """用户仪表盘"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@auth_bp.route('/admin/dashboard')
def admin_dashboard():
    """管理员仪表盘"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.admin_login'))
    
    admin = User.query.get(session['user_id'])
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin_dashboard.html', admin=admin, users=users)

@auth_bp.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('auth.login'))

# ==================== 首页 ====================

@auth_bp.route('/')
def index():
    """首页 - 直接跳转到登录页"""
    return redirect(url_for('auth.login'))
