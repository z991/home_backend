from django.contrib.auth.models import User
from applications.user_manage.base_views import get_member


class SuperAdmin(object):
    def __init__(self):
        self.admin_tool = {"超级管理员"}
        self.isteraton_tool = set()

    # 获取oa_platform数据库分组是管理员的所有用户名
    def get_tool_is_admin(self):
        user_admin = User.objects.filter(groups__name="管理员")
        for user in user_admin:
            self.admin_tool.add(getattr(user, 'last_name'))
        return self.admin_tool

    # 获取oa_platform数据库分组是行政的所有用户名
    def get_tool_is_administrative(self):
        administrative = User.objects.filter(groups__name="行政")
        for item in administrative:
            self.isteraton_tool.add(getattr(item, 'last_name'))
        return self.isteraton_tool


def validate_superadmin(request):
    # 获取ldap-admin分组下的所有用户(中文名)
    role = 'ldap-admin'
    group = 'LDAP'
    member = get_member(role, group)
    if not isinstance(member, list):
        member = []
    super_admin = SuperAdmin()
    last_name = getattr(request.user, 'last_name')
    if last_name in (super_admin.get_tool_is_admin() and member):
        return True
    return False


def validate_ldap(request):
    role = 'ldap-admin'
    group = 'LDAP'
    ldap_admin = get_member(role, group)
    if not isinstance(ldap_admin, list):
        ldap_admin = []
    super_admin = SuperAdmin()
    last_name = getattr(request.user, 'last_name')
    if (last_name in super_admin.get_tool_is_admin()) \
            or (last_name in super_admin.get_tool_is_administrative())\
            or (last_name in ldap_admin):
        return True
    return False