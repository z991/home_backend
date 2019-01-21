# 日志模块
MODULES_MAP = {
"groupviewset-update": "角色修改",
    "groupviewset-create": "角色新增",
    "groupviewset-get_queryset": "搜索角色和查看人员的角色列表",
    "userviewset-get_user_perm": "获取权限",

    "user_list": "查看用户列表",
    "user_detail": "查看用户详情",
    "user_add": "用户新增",
    "user_delete": "用户删除",
    "user_put": "用户修改",

    "RolesViewSet": "系统列表   ",
    "RolesDetailSet": "系统删除",

    "list_roles": "展示角色类别",
    "list_role": "展示角色",
    "list_group_roles": "展示角色组",
    "list_role_members": "展示角色成员",
    "list_user_role": "人员角色查看",
    "delete_role_members": "删除角色成员",
    "update_role_members": "编辑角色成员",
    "create_role_members": "添加角色成员",

    "personal_changepassword": "修改个人密码",
    "change_role": "修改角色名称",
    "change_group": "修改系统名称",

    "systemlogviewset-get_queryset": "查看系统日志",
    "personallogviewset-get_queryset": "查看个人日志",

    "get_myfavourite": "查看我的收藏",
    "post_myfavourite": "添加我的收藏",
    "delete_myfaourite": "删除我的收藏",
    "set_sort": "个性化设置",
    "modeltype-list": "查看导航展示页面",
}

# 日志类型
TYPE_POST = 1
TYPE_DELETE = 2
TYPE_PUT = 3
TYPE_LOGIN = 4
TYPE_LOGOUT = 5
TYPE_VIEW = 6
TYPE_ELSE = 500
LOG_TYPE_CHOICES = (
    (TYPE_POST, "新增"),
    (TYPE_DELETE, "删除"),
    (TYPE_PUT, "修改"),
    (TYPE_LOGIN, "登录"),
    (TYPE_LOGOUT, "退出"),
    (TYPE_VIEW, "查看"),
    (TYPE_ELSE, "其他"),
)

ACTION_MAP = {
    "POST": TYPE_POST,
    "PUT": TYPE_PUT,
    "DELETE": TYPE_DELETE,
    "GET": TYPE_VIEW,
}

# 发送邮件配置
SENDER = 'sport@xiaoneng.cn'
MAIL_HOST = "smtp.exmail.qq.com"
MAIL_USER = "sport@xiaoneng.cn"
MAIL_PASS = "xiaoneng.2015"
