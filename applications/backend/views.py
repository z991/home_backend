from django.http.response import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from passlib.hash import ldap_salted_sha1 as sha
from rest_framework import status
import json

from applications.backend.models import LdapUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from applications.user_manage.base_views import get_member
from applications.log_manage.models import OperateLog

@csrf_exempt
# @api_view(['POST'])
def login(request):
    """
    author:zxy
    function:登录先验证ldap再验证本地
    param :request 前端发来的请求
    return: 以user.id为内容的JsonResponse
    """
    # 判断请求类型
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    bod = request.body
    bod = str(bod, encoding="utf-8")
    params = json.loads(bod)
    post_code = params.get("check_code", "").lower()
    session_code = request.session.get('verifycode', "").lower()
    username = params.get("username", "")
    # 输入的密码
    password = params.get("password", "")
    # 判断验证码
    if (not post_code) or (session_code != post_code):
        return JsonResponse({"error": "验证码错误"}, status=status.HTTP_417_EXPECTATION_FAILED, safe=False)
    try:
        user_ldap = LdapUser.objects.get(username=username)
        u_password = user_ldap.password
        very_ldap = sha.verify(password, u_password)
        if very_ldap == True:
            user = User.objects.get(username=user_ldap)
            auth.login(request, user)
        else:
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                return JsonResponse({'error': '该用户不存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            local_password = user.password
            very = sha.verify(password, local_password)
            if very == False:
                return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
            auth.login(request, user)

    except Exception as e:
        return JsonResponse({'error': '该用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
    OperateLog.login(request)
    return JsonResponse({"id": user.id}, status=status.HTTP_200_OK)


@csrf_exempt
def logout(request):
    """
    function:登出
    param: request
    return:
    """
    if not request.method == "GET":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    auth.logout(request)
    OperateLog.logout(request)
    return HttpResponse('success', status=status.HTTP_200_OK)


@api_view(['GET'])
def account_permission(request):
    account = {"person_set": {"view": 1},
               "password": {"view": 1},
               "curd_user": {"view": 0},
               "curd_group": {"view": 0},
               "log": {"view": 0}}
    user = request.user.last_name
    role = 'ldap-admin'
    group = 'LDAP'
    member = get_member(role, group)
    if user in member:
        account["curd_user"]["view"] = 1
        account["curd_group"]["view"] = 1
        account["log"]["view"] = 1
    return JsonResponse(account, status=status.HTTP_200_OK)