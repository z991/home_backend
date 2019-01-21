import json
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from applications.navigation.serializers import TypeSerializer
from applications.navigation.models import ModelType, Navigations, SortInfo, UserFaviourt
from applications.log_manage.models import OperateLog

# Create your views here.

# 我的收藏展示接口
@api_view(['GET'])
def get_myfavourite(request):
    OperateLog.create_log(request)
    date = []
    host = str(request.get_host())
    username_id = request.user.id
    if username_id:
        queryset = Navigations.objects.filter(navigation_fav__user_faviourt=username_id).distinct()
        for i in queryset:
            id = i.id
            name = i.name_navigations
            url = i.url

            image = 'http://' + host+'/upload/'+str(i.image)
            desc = i.desc
            date.append({"id": id,
                         "name_navigations": name,
                         "url": url,
                         "image": image,
                         "desc": desc})
    else:
        return JsonResponse({"error": "请登录"}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"date": date}, status=status.HTTP_200_OK)


# 我的收藏添加接口
@csrf_exempt
def post_myfavourite(request):
    OperateLog.create_log(request)
    if not request.method == "POST":
        return JsonResponse({"error": "请求方式不正确"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    user = request.user
    if str(user) == 'AnonymousUser':
        return JsonResponse({"error": "请先登录"}, status=status.HTTP_400_BAD_REQUEST)
    bod = request.body
    bod = str(bod, encoding="utf-8")
    params = json.loads(bod)
    na_id = params.get("na_id")
    naviagetion = Navigations.objects.get(pk=na_id)

    user_favriout = UserFaviourt.objects.filter(user_faviourt=user).exists()
    if not user_favriout:
        fa = UserFaviourt.objects.create(user_faviourt=user)
    faviourt = UserFaviourt.objects.get(user_faviourt=user)

    queryset = Navigations.objects.filter(navigation_fav__user_faviourt=user.id).distinct()
    for i in queryset:
        if i.id == int(na_id):
            return JsonResponse({"error": "不能重复收藏"}, status=status.HTTP_400_BAD_REQUEST)
    faviourt.faviourt.add(naviagetion)
    return JsonResponse({"info": "收藏成功"}, status=status.HTTP_200_OK)


# 我的收藏删除接口
@csrf_exempt
def delete_myfaourite(request):
    OperateLog.create_log(request)
    if not request.method == "DELETE":
        return JsonResponse({"error": "请求方式不正确"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    na_id = request.GET.get("na_id")
    user = request.user
    favorite = UserFaviourt.objects.get(user_faviourt=user)
    navigation = Navigations.objects.get(pk=na_id)
    favorite.faviourt.remove(navigation)
    return JsonResponse({"info": "取消收藏成功"}, status=status.HTTP_200_OK)


# 排序设置
@csrf_exempt
def set_sort(request):
    OperateLog.create_log(request)
    if not request.method == "POST":
        return JsonResponse({"error": "请求方式不正确"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    user = request.user
    bod = request.body
    bod = str(bod, encoding="utf-8")
    params = json.loads(bod)
    # {"1": "类型id"}
    try:
        sort_info = params.get("sort_info")
        sort_dict = {
            "username": user,
            "order": sort_info
        }
        ex = SortInfo.objects.filter(username=user).exists()
        if ex:
            SortInfo.objects.filter(username=user).update(order=sort_info)
        else:
            SortInfo.objects.create(**sort_dict)
    except Exception as e:
        return JsonResponse({"error": "设置失败", "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"info": "设置成功"}, status=status.HTTP_200_OK)


# 导航展示页面
class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    导航模块
    '''
    pagination_class = None
    queryset = ModelType.objects.all().order_by("-id")
    serializer_class = TypeSerializer

    def list(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data_list = []
        s = 0
        user = request.user
        print('user', user, type(user))
        if str(user) == 'AnonymousUser':
            for ds in data:
                s += 1
                data_list.append({"la": 1, "ch": ds})
            return Response(data_list, status=status.HTTP_200_OK)
        else:
            # 获取存储的所有排序
            data_list = []
            sort_info = SortInfo.objects.filter(username=user).first()

            # 判断sort_info为空
            s = 0
            if sort_info == None:
                for ds in data:
                    s = s + 1
                    data_list.append({"la": s, "ch": ds})
            # 如果排序不为空
            else:
                sort_info = sort_info.order
                sort_info = eval(sort_info)
                # 所有type的id集合
                type_id = set()
                for d in data:
                    type_id.add(d["id"])

                # 获取排序的id
                sort_id = set()
                for s, t in sort_info.items():
                    sort_id.add(t)

                # 获取未排序的id
                df_id = type_id - sort_id
                print('df_id', df_id)

                # 获取排序的元素
                for j, q in sort_info.items():
                    for i in data:
                        if i["id"] == q:
                            data_list.append({"la": j, "ch": i})

                # 为n赋值，大于df_id的最大值
                n = int(j)
                # 添加未排序的type
                for df in df_id:
                    for da in data:
                        if int(df) == int(da["id"]):
                            n = n + 1
                            data_list.append({"la": n, "ch": da})
            return Response(data_list)
