from .common import connect_ldap
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from .models import LdapUser, LdapGroup, LdapRoles, LdapOA
from .serializers import Userserializer, Groupserializer, Rolesserializer, OAserializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.http import JsonResponse
from applications.log_manage.models import OperateLog
from .view_admin import validate_ldap


# 解决csrf
class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    参考http://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    """
    def enforce_csrf(self, request):
        return


# 系统新增&列表
class RolesViewSet(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        Roles = LdapRoles.objects.all()
        serilazier = Rolesserializer(Roles, many=True)
        OperateLog.create_log(request)
        return Response(serilazier.data)

    def post(self, request, format=None):
        if not validate_ldap(request):
            return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
        OperateLog.create_log(request)
        data = request.data
        cn = data["cn"]
        roles = LdapRoles.objects.all()
        for i in roles:
            if i.cn == cn:
                return JsonResponse({"error": "该系统已存在无法添加"}, status=status.HTTP_400_BAD_REQUEST)
        serilzazier = Rolesserializer(data=request.data)

        if serilzazier.is_valid():
            serilzazier.save()
            return JsonResponse({"info": "新增成功"}, status=status.HTTP_201_CREATED)
        return Response(serilzazier.errors, status=status.HTTP_400_BAD_REQUEST)


# 系统删除
class RolesDetailSet(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_object(self, pk):
        return LdapRoles.objects.get(pk=pk)

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = Rolesserializer(user)
        OperateLog.create_log(request)
        return Response(serializer.data)

    def delete(self, request, format=None):
        if not validate_ldap(request):
            return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
        pk = self.request.GET.get("pk", '')
        user = self.get_object(pk)
        try:
            with connect_ldap() as c:
                user.delete()
                OperateLog.create_log(request)
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": "该系统下有角色,请先删除角色"}, status=status.HTTP_400_BAD_REQUEST)


# 修改系统名称
@api_view(['GET'])
def change_group(request):
    if not validate_ldap(request):
        return JsonResponse({"error": "您没权限"}, status=status.HTTP_403_FORBIDDEN)
    request.method = 'PUT'
    OperateLog.create_log(request)
    group = request.GET.get('group', '')
    new_group = request.GET.get('new_group', '')
    try:
        data2 = LdapRoles.objects.all().filter(cn=group).values_list('cn', 'dn')
        _cn, _dn = data2[0]
        instance = LdapRoles.objects.all().get(dn=_dn)
        instance.cn = new_group
        instance.save()
        result = {"result": True, "message": ""}
        request.method = 'PUT'
        return Response(result)
    except Exception as e:
        result = {"result": False, "message": str(e.args)}
        return Response(result)
