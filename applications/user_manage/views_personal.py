import logging
import ast

from passlib.hash import ldap_salted_sha1 as sha
from ldap3 import MODIFY_REPLACE, SUBTREE
from .common import connect_ldap
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.models import User

from applications.log_manage.models import OperateLog

log = logging.getLogger('django')


@csrf_exempt
def personal_changepassword(request):
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    data = ast.literal_eval(request.body.decode('utf-8'))
    OperateLog.create_log(request)
    try:
        with connect_ldap() as c:
            c.search('ou=Users,dc=xiaoneng,dc=cn',
                     search_filter='(objectClass=inetOrgPerson)',
                     attributes=['userPassword', 'cn'],
                     search_scope=SUBTREE)
            ldap_password = ''
            dn = ''
            for i in c.entries:
                cn = i.entry_attributes_as_dict['cn'][0]
                print(cn)
                if i.entry_attributes_as_dict['cn'][0] == request.user.get_username():
                    ldap_password = i.entry_attributes_as_dict['userPassword'][0]
                    dn = i.entry_dn
                    break
            if ldap_password and sha.verify(data['old_password'], ldap_password):
                c.modify(dn, {'userpassword': [(MODIFY_REPLACE, sha.hash(data['new_password']))]})
                # 修改本地密码
                user = User.objects.get(username=cn)
                user.password = sha.hash(data['new_password'])
                user.save()
            else:
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                                    data={"result": False, "error": '旧密码错误, 验证失败'})

        return JsonResponse(status=status.HTTP_200_OK,
                            data={"result": True, "message": "修改成功"})
    except Exception as e:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                            data={"result": False, "error": str(e.args)})
