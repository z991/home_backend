import logging
import ast

from ldap3 import SUBTREE, MODIFY_REPLACE
from .common import connect_ldap

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from applications.log_manage.models import OperateLog
from .models import LdapRoleGroup
from .view_admin import validate_ldap
from applications.user_manage.base_views import get_group_role, get_member
log = logging.getLogger('django')


# 展示角色类别
@api_view(['GET'])
def list_roles(request):
    OperateLog.create_log(request)
    try:
        response = []
        with connect_ldap() as c:
            c.search('ou=Roles, dc=xiaoneng, dc=cn', search_filter='(objectClass=organizationalRole)',
                     attributes=['cn'], search_scope=SUBTREE)

            for i in c.entries:
                d = {
                    "cn": i.entry_attributes_as_dict['cn'][0],
                    "dn": i.entry_dn,
                }
                response.append(d)
        return Response(response)
    except Exception as e:
        return Response({"result": False, "error": str(e.args)})


# 展示角色
@api_view(['GET'])
def list_role(request):
    role = request.GET.get("role", "")
    try:
        response = []
        with connect_ldap() as c:
            c.search('cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % role, search_filter='(objectClass=groupOfUniqueNames)',
                     attributes=['cn'],
                     search_scope=SUBTREE)

            for i in c.entries:
                d = {
                    "cn": i.entry_attributes_as_dict['cn'][0],
                    "dn": i.entry_dn,
                }
                response.append(d)
        return Response(response)
    except Exception as e:
        return Response({"result": False, "error": str(e.args)})


# 展示角色组(所有角色)
@api_view(['GET'])
def list_group_roles(request):
    result = get_group_role()
    if isinstance(result, list):
        request.method = 'GET'
        return Response(result)
    if isinstance(result, str):
        return Response({"result": False, "error": result})


# 展示角色成员
@api_view(['GET'])
def list_role_members(request):
    OperateLog.create_log(request)
    role = request.GET.get('role')
    group = request.GET.get('group')
    result = get_member(role, group)
    if isinstance(result, list):
        return Response(result)
    if isinstance(result, str):
        return Response({"result": False, "error": result})


# 人员角色查看(查看某个人的所有分组)
@api_view(['GET'])
def list_user_role(request):
    OperateLog.create_log(request)
    user = request.GET.get('user')
    try:
        with connect_ldap() as c:
            c.search('cn=%s,ou=Users,dc=xiaoneng,dc=cn' % user,
                     attributes=['sn', 'memberOf'], search_filter='(objectClass=inetOrgPerson)')
            members = {'role':[]}
            for i in c.entries:
                members['name'] = (i.entry_attributes_as_dict['sn'][0])
                members['role'].append(i.entry_attributes_as_dict['memberOf'])
        return Response(members)
    except Exception as e:
        return Response({"result": False, "error": str(e.args)})


# 删除角色成员
@api_view(['GET'])
def delete_role_members(request):
    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
    request.method = 'DELETE'
    OperateLog.create_log(request)
    role = request.GET.get('role')
    group = request.GET.get('group')

    try:
        with connect_ldap() as c:
            c.delete('cn=%s,cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (role, group))
            log.info(c.result)
            if 'result' in c.result and c.result['result'] == 0:
                result = {"result": True, "message": ""}
            else:
                result = {"result": False, "message": c.result['message']}
        return Response(result)
    except Exception as e:
        return Response({"result": False, "error": str(e.args)})


# 编辑列表
@api_view(['GET'])
def left_right_list(request):
    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
    role = request.GET.get('role')
    group = request.GET.get('group')
    if (None == role) or (None == group):
        return Response({"result": False, "error": '参数缺失或错误'})
    name_dict = get_role_name(role, group)
    all_mem = all_member()
    if name_dict['message']:
        member_list = name_dict['result']
        right_list = list(member_list.keys())
        all_name = list(all_mem.keys())
        left_list = list(set(all_name).difference(set(right_list)))

        non_member_dict = {}
        for i in left_list:
            non_member_dict[i] = all_mem[i]

        data = {'members': member_list, 'non_member': non_member_dict}
        return Response({'result': True, 'data': data})
    else:
        return Response({"result": False, "data": name_dict['result']})


# 获取该角色的成员
def get_role_name(*args):
    name_list = {"message": False, "result": {}}
    role, group = args
    search_base = 'cn=%s,cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (role, group)
    try:
        with connect_ldap() as c:
            c.search(search_base=search_base,
                     search_filter='(objectClass=groupOfUniqueNames)',
                     attributes=['*'])

            list = c.response[0]['attributes']['uniqueMember']
            list_name = []
            new_list = []
            for i in list:
                c.search(i, search_filter='(objectClass=inetOrgPerson)', attributes=['sn'])
                if c.response==[]:
                    continue
                list_name.append(c.response[0]['attributes']['sn'][0])
                new_list.append(c.response[0]['dn'])

            name_list['result'] = dict(zip(list_name, new_list))
            name_list['message'] = True
        return name_list
    except Exception as e:
        name_list['result'] = {'data': (str(e.args))}
        return name_list


# 所有的人
def all_member():
    try:
        with connect_ldap() as c:
            c.search('ou=Users,dc=xiaoneng,dc=cn',
                     search_filter='(objectClass=inetOrgPerson)',
                     attributes=['*'])
            all_member_name = []
            all_member_dn = []
            for i in c.entries:
                all_member_dn.append(i.entry_dn)
                all_member_name.append(i.entry_attributes_as_dict['sn'][0])
        return dict(zip(all_member_name, all_member_dn))
    except Exception as e:
        return str(e.args)


# 编辑角色成员
@csrf_exempt
def update_role_members(request):
    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
    request.method = 'PUT'
    OperateLog.create_log(request)
    # params = {'role': 'csc',
    #           'group': 'OA',
    #           'members': ["cn=wangliying,ou=Users,dc=xiaoneng,dc=cn",
    #                       "cn=liyuyan,ou=Users,dc=xiaoneng,dc=cn",
    #                       "cn=liyuzhen,ou=Users,dc=xiaoneng,dc=cn"]}
    params = ast.literal_eval(request.body.decode('utf-8'))
    role = params['role']
    group = params['group']

    try:
        with connect_ldap() as c:
            if params['members']:
                modify = (MODIFY_REPLACE, params['members'])
            else:
                modify = (MODIFY_REPLACE, [])
            c.modify('cn=%s,cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (role, group),
                     {'uniqueMember': [modify]})
            log.info(c.result)
            if c.result['result'] != 0:
                raise Exception("成员修改失败!")

        return JsonResponse(status=status.HTTP_200_OK, data={"result": True, "error": ''})
    except Exception as e:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": str(e.args)})


# 添加角色
@csrf_exempt
def create_role_members(request):
    request.method = 'POST'
    OperateLog.create_log(request)
    params = ast.literal_eval(request.body.decode('utf-8'))
    group = params['group']
    name = params['name']
    result = []
    try:
        with connect_ldap() as c:
            c.search('cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % group, search_filter='(objectClass=groupOfUniqueNames)',
                     attributes=['cn'],
                     search_scope=SUBTREE)
            for i in c.entries:
                result.append(i.entry_attributes_as_dict['cn'][0])
    except Exception as e:
        return Response({"result": False, "error": str(e.args)})
    if name in result:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data={"error": '角色名称不能重复'})

    try:
        with connect_ldap() as c:
            c.add('cn=%s,cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (name, group),
                  ['groupOfUniqueNames', 'top'], {'uniqueMember': ['cn=neo,ou=Users,dc=xiaoneng,dc=cn']})
            log.info(c.result)
            if 'result' in c.result and c.result['result'] == 0:
                result = {"result": True, "message": ""}
            else:
                result = {"result": False, "message": c.result['message']}
        return JsonResponse(status=status.HTTP_200_OK, data=result)
    except Exception as e:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data={"result": False, "error": str(e.args)})


# 修改角色名称
@api_view(['GET'])
def change_role(request):
    group = request.GET.get('group', '')
    role = request.GET.get('role', '')
    new_role = request.GET.get('new_role', '')
    try:
        dn = 'cn=%s, cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (role, group)
        instance = LdapRoleGroup.objects.all().get(dn=dn)
        instance.cn = new_role
        try:
            instance.save()
        except:
            pass
        request.method = 'PUT'
        OperateLog.create_log(request)

        result = {"result": True, "message": "Ok"}
        return Response(result)
    except Exception as e:
        result = {"result": False, "message": str(e.args)}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
