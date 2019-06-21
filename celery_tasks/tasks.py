# 使用celery
from django.core.mail import send_mail
from celery import Celery
from django.conf import settings
import time

# # 任务处理者加
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()


# 创建一个celery实例对象
app = Celery('celery_tasks.tasks', broker='redis://10.112.95.196:6379/8')


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    # 发送激活邮件
    subject = '天天生鲜欢迎您'
    message = ''
    sender = settings.EMAIL_FROM
    recevier = [to_email]
    html_message = '<h1>欢迎尊贵的%s成为天天生鲜顶级会员</h1>请点击下面链接激活您的账号<br/><a ' \
                   'href=http://127.0.0.1:8000/user/active/%s>http://127.0.0.1:8000/user' \
                   '/active/%s</a>' % (username, token, token)

    send_mail(subject, message, sender, recevier, html_message=html_message)
    time.sleep(5)