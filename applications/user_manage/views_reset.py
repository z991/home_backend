import logging
import time
import traceback
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from passlib.hash import ldap_salted_sha1 as sha
from .smtp_email import send_mail
from .common import connect_ldap
from ldap3 import MODIFY_REPLACE, SUBTREE
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from applications.user_manage.base_views import verifycode
from libs.hash import encrypt, decrypt

log = logging.getLogger('django')
vaild_secret = 'CIUTrGAqxFjtBOnE'


@csrf_exempt
def resetpasswd_url(request):
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    bod = request.body
    bod = str(bod, encoding="utf-8")
    params = json.loads(bod)
    username = params.get('username', '')
    email = str(username) + '@xiaoneng.cn'
    text = ':'.join([username, email, str(time.time())])
    encry_str = encrypt(text)
    request.session['aeskey'] = str(encry_str, 'utf-8')
    code = verifycode(request)
    if send_mail(email, code):
        data = {"result": True, "error": "邮件已经发送至{}!".format(email)}
        return JsonResponse(status=status.HTTP_200_OK, data=data)
    else:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "邮件发送失败，请重试"})


@api_view(['GET'])
@permission_classes((AllowAny, ))
def verify_code(request):
    code = request.GET.get('code', '')
    verify_code = request.session.get('verifycode', "").lower()
    aeskey = request.session.get('aeskey', '')

    if aeskey:
        decry_str = decrypt(aeskey)
        req_timestamp = decry_str.split(':')[2]
        if time.time() - float(req_timestamp) > 3600:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "重置链接超时"})
        if code == verify_code:
            decry_str = decrypt(aeskey)
            username = decry_str.split(':')[0]
            now_time = decry_str.split(':')[2]
            new_key = encrypt(':'.join([username, code, now_time]))
            request.session['aeskey'] = 'haha'
            return Response(status=status.HTTP_200_OK, data={"result": new_key, "error": "验证码校验成功"})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "验证码不正确"})


@api_view(['GET'])
@permission_classes((AllowAny, ))
def reset(request):
    passwd = sha.hash(request.GET.get('password', ''))
    if not passwd:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "密码输入为空!"})
    # aeskey = request.session.get('aeskey', '')
    aeskey = request.GET.get('new_key', '')
    if aeskey:
        decry_str = decrypt(aeskey)
        username = decry_str.split(':')[0]
        req_timestamp = decry_str.split(':')[2]
        if time.time() - float(req_timestamp) > 3600:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "重置链接超时"})
        else:
            try:
                with connect_ldap() as ldap_conn:
                    ldap_conn.search(search_base='ou=Users,dc=xiaoneng,dc=cn',
                                     search_filter='(objectClass=inetOrgPerson)',
                                     search_scope=SUBTREE,
                                     attributes=['userPassword', 'cn'])
                    for entry in ldap_conn.entries:
                        if entry.entry_attributes_as_dict['cn'][0] == username:
                            ldap_conn.modify(entry.entry_dn, {'userpassword': [(MODIFY_REPLACE, passwd)]})
                            if ldap_conn.result['result'] == 0:
                                return Response({"result": True, "error": "密码重置成功"})
                            else:
                                data = {"result": False, "error": "str(ldap_conn.result['message'])"}
                                return Response(status=status.HTTP_400_BAD_REQUEST, data=data)
            except Exception as e:
                traceback.print_exc()
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": str(e.args)})
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": "未获取到令牌"})
