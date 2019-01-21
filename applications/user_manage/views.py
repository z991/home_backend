import re
import logging
import json

from django.http import JsonResponse
from applications.user_manage.base_views import member_clear
from ldap3 import MODIFY_ADD, SUBTREE, MODIFY_REPLACE, MODIFY_DELETE
from django.views.decorators.csrf import csrf_exempt
from .common import connect_ldap
from rest_framework.response import Response
from rest_framework import status
from passlib.hash import ldap_salted_sha1 as sha
from rest_framework.decorators import api_view
from applications.log_manage.models import OperateLog
from .view_admin import validate_ldap
from .models import LdapUser
from django.contrib.auth.models import User
from applications.user_manage.base_views import get_group_role, update_info,\
    dn_update_permission, permission_update_dn
from applications.user_manage.base_views import get_member, get_user_role
log = logging.getLogger('django')


# 用户列表
@api_view(['GET'])
def user_list(request):
    # 前端传过来的页码
    OperateLog.create_log(request)
    page = request.GET.get('page', 1)
    page = int(page)

    if page == 1:
        start = 0
        end = 10
    else:
        start = 10 * (page - 1)
        end = 10 * page
    # 获取ldap-admin用户
    role = 'ldap-admin'
    group = 'LDAP'
    member = get_member(role, group)

    user = request.user.username

    rdn = 'ou=Users,dc=xiaoneng,dc=cn'
    reg = re.compile('.*?ou=(.*?),')
    try:
        single_result = []
        result = []
        with connect_ldap() as c:
            c.search(rdn, search_filter='(objectClass=inetOrgPerson)', attributes=['sn', 'cn', 'mail'],
                     search_scope=SUBTREE)
            # {'attributes': {'sn': ['二狗子']},
            #  'dn': 'cn=ergouzi,ou=运维,ou=Users,dc=xiaoneng,dc=cn',
            #  'raw_attributes': {'sn': [b'\xe4\xba\x8c\xe7\x8b\x97\xe5\xad\x90']},
            #  'type': 'searchResEntry'}
            num = 0
            for i in c.entries:
                num += 1
                dn = i.entry_dn
                group = dn[0:-1 * len(rdn)]
                m = reg.match(group)
                d = {
                    "cn": i.entry_attributes_as_dict['cn'][0],
                    "sn": i.entry_attributes_as_dict['sn'][0],
                    "dn": i.entry_dn,
                    "mail": i.entry_attributes_as_dict['mail'][0] if i.entry_attributes_as_dict['mail'] else '',
                    "index": num
                }
                if d.get("cn") == user:
                    single_result.append(d)
                result.append(d)
            # 结果总个数
            total_count = num

            # 获取总页数
            total_page = total_count // 10
            total_page = total_page + 1

            total_result = result
            if request.user.last_name not in member:
                result = single_result
            else:
                result = result[start:end]
            return Response({"total_count": total_count, "total_page": total_page,
                             "result": result, "total_result": total_result}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户详情
@api_view(['GET'])
def user_detail(request):
    OperateLog.create_log(request)
    user = request.GET.get("user", "")
    try:
        with connect_ldap() as c:
            c.search('cn=%s,ou=Users,dc=xiaoneng,dc=cn' % user,
                     search_filter='(objectClass=inetOrgPerson)',
                     attributes=['sn', 'cn', 'mail', 'memberof'])
            # 获取所有角色（所有角色）
            ret = get_group_role()
            if not isinstance(ret, list):
                return Response({"error": ret}, status=status.HTTP_400_BAD_REQUEST)

            # 获取总的分组以及角色字典
            permissions_dict = update_info(ret)
            # 获取某个人的所有权限，并对字典赋值
            result = {}
            for item in c.entries:
                memberof = item.entry_attributes_as_dict['memberOf']
                print('zxymemberof', memberof)
                result.update({
                    "cn": item.entry_attributes_as_dict['cn'][0],
                    "sn": item.entry_attributes_as_dict['sn'][0],
                    "mail": item.entry_attributes_as_dict['mail'][0],
                    "permission": dn_update_permission(memberof, permissions_dict)
                })
            return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户新增
@csrf_exempt
def user_add(request):
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})

    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)

    bod = request.body
    bod = str(bod, encoding="utf-8")
    data = json.loads(bod)
    OperateLog.create_log(request)

    cn = data['cn']
    exits = LdapUser.objects.filter(username=cn).count()
    # TODO 这个查询只会找 oa_platform 的 AUTH_USER 表
    if exits > 0:
        return JsonResponse({"error": "该用户已存在"}, status=status.HTTP_400_BAD_REQUEST)

    permission_dict = dict(data.get('permission'))

    try:
        with connect_ldap() as c:
            base_dn = 'cn=%s, ou=Users,dc=xiaoneng,dc=cn' % cn
            permission_list = permission_update_dn(permission_dict)
            print('per', permission_list)

            c.add(base_dn,
                  ['inetOrgPerson', 'top', 'ldapPublicKey'],
                  {'sn': data['sn'],
                   'mail': '%s@xiaoneng.cn' % data['cn'],
                   "userpassword": sha.hash(data['password']),
                   "sshPublicKey": data.get('sshPublicKey', ''),
            })
            for role in permission_list:
                role = role.replace(",ou=Users,", ",ou=Roles,")
                c.modify(role, {'uniqueMember': [(MODIFY_ADD, base_dn)]})
            c.modify('cn=users,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn', {'uniqueMember': [(MODIFY_ADD, base_dn)]})
            return JsonResponse({"info": "新增成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "新增失败", "message": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户修改
@csrf_exempt
def user_put(request):
    """
    :param request: sn, permission_list,cn
    :return: None
    modify_mail = (MODIFY_REPLACE, data['mail'])
    c.modify(dn, {'sn': [modify_sn], 'mail': modify_mail})
    """
    if not request.method == "PUT":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)

    bod = request.body
    bod = str(bod, encoding="utf-8")
    data = json.loads(bod)
    permission_info = dict(data.get('permission'))
    permission_list = permission_update_dn(permission_info)
    OperateLog.create_log(request)
    try:
        with connect_ldap() as c:
            dn = "cn=%s,ou=Users,dc=xiaoneng,dc=cn" % data['cn']
            modify_sn = (MODIFY_REPLACE, data['sn'])

            c.modify(dn, {'sn': [modify_sn]})
            # TODO memberOf 有坑
            result = get_user_role(data['cn'])
            if isinstance(result, dict):
                for each in result['role']:
                    role = each.replace(",ou=Users,", ",ou=Roles,")
                    c.modify(role, {'uniqueMember': (MODIFY_DELETE, [dn])})

            if isinstance(result, str):
                return JsonResponse({"error": "修改失败", "message": result}, status=status.HTTP_400_BAD_REQUEST)

            for item in permission_list:
                role = item.replace(",ou=Users,", ",ou=Roles,")
                c.modify(role, {'uniqueMember': (MODIFY_ADD, [dn])})
            return JsonResponse({"info": "修改成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "修改失败", "message": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户删除
@csrf_exempt
def user_delete(request):
    if not request.method == "DELETE":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    if not validate_ldap(request):
        # 验证ldap_admin 和 oa_admin 和 oa-行政组
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
    OperateLog.create_log(request)
    cn = request.GET.get('cn', '')
    try:
        with connect_ldap() as c:
            # 清除用户所有角色后删除
            member_clear(cn)
            c.delete("cn=%s,ou=Users,dc=xiaoneng,dc=cn" % cn)
            ret = User.objects.filter(username=cn).delete()
            return JsonResponse({"message": "删除成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "删除失败: " + str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_permission(request):
    result = get_group_role()
    print('result', result, type(result))
    if not isinstance(result, list):
        return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
    ret = update_info(result)
    return Response(data=ret, status=status.HTTP_200_OK)