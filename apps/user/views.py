from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from user.models import User
from celery_tasks.tasks import send_register_active_email
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired


# Create your views here.
def register(request):
    """注册"""
    if request.method == "GET":
        # 显示注册页面
        return render(request, 'register.html')
    else:
        # 进行注册处理
        # 1.接受数据
        user_name = request.POST.get("user_name")
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        cpwd = request.POST.get('cpwd')
        allow = request.POST.get('allow')

        # 2.数据校验
        if not all([user_name, password, email, cpwd]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验两次输入密码
        if cpwd != password:
            return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

        # 校验是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(user_name, email, password)
        user.is_active = 0
        user.save()

        # 4.返回应答:跳转到首页
        return redirect(reverse('goods:index'))


class RegisterView(View):
    """注册"""

    def get(self, request):
        # 显示注册页面
        return render(request, 'register.html')

    def post(self, request):
        # 进行注册处理
        # 接收数据
        user_name = request.POST.get("user_name")
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        cpwd = request.POST.get('cpwd')
        allow = request.POST.get('allow')

        # 2.数据校验
        if not all([user_name, password, email, cpwd]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验两次输入密码
        if cpwd != password:
            return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

        # 校验是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(user_name, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接：/user/active/1
        # 激活链接中包含用户的身份信息,并且身份信息加密

        # 加密用户的身份信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # bytes
        token = token.decode()

        # 发邮件
        send_register_active_email.delay(email, user_name, token)

        # 4.返回应答:跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        # 进行用户激活
        # 进行解密，获取要激活用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()


            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# user/login
class LoginView(View):
    """登录"""

    def get(self, request):
        # 显示登录页面
        return render(request, 'login.html')
