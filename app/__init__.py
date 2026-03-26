from flask import Flask
from config import Config
from app.models import db
from flask_mail import Mail

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化邮箱服务
    mail.init_app(app)
    
    # 创建所有表
    with app.app_context():
        db.create_all()
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app
