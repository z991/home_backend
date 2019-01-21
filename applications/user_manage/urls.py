from django.conf.urls import url, include
from rest_framework import routers

from . import views, views_role, views_group, views_reset, views_personal

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    # 用户列表
    url(r'^user_list/$', views.user_list),
    # 用户详情
    url(r'^user_detail/$', views.user_detail),
    # 用户组列表&新增
    url(r'^user_add/$', views.user_add),
    # 用户修改
    url(r'^user_put/$', views.user_put),
    # 用户删除
    url(r'^user_delete/$', views.user_delete),
    # 所有权限展示接口
    url(r'^all_permission', views.get_all_permission),
    # 用户组列表&新增
    url(r'^group_list/$', views_group.RolesViewSet.as_view()),
    # 用户组删除接口
    url(r'^group_detail/$', views_group.RolesDetailSet.as_view()),

    # 展示角色类别
    url(r'^list_roles/$', views_role.list_roles),
    # 根据分组展示角色
    url(r'^list_role/$', views_role.list_role),
    # 展示角色组
    url(r'^list_group_roles/$', views_role.list_group_roles),
    # 删除角色成员
    url(r'^delete_role_members/$', views_role.delete_role_members),
    # 展示角色成员
    url(r'^list_role_members/$', views_role.list_role_members),
    # 编辑角色成员
    url(r'^update_role_members/$', views_role.update_role_members),
    # 新增角色成员
    url(r'^create_role_members/$', views_role.create_role_members),
    # 人员角色查看
    url(r'^list_user_role/$', views_role.list_user_role),
    # 编辑前左右列表
    url(r'^left_right_list/$', views_role.left_right_list),

    # views_reset
    url(r'^reset_passwd/$', views_reset.resetpasswd_url),
    url(r'^reset/$', views_reset.reset),
    url(r'^verify_code/$', views_reset.verify_code),
    # 个人修改密码
    url(r'^change_pwd/$', views_personal.personal_changepassword),
    # 修改系统名称
    url(r'^change_group/$', views_group.change_group),
    # 修改角色名称
    url(r'^change_role/$', views_role.change_role),

]
api_urls = router.urls + urlpatterns