from django.urls import path
from django.conf import settings
from django.views.static import serve  # 处理静态/媒体文件的核心视图

from web.views.index import index
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView
from web.views.user.account.get_user_info import GetUserInfoView

urlpatterns = [
    path('api/user/account/login/', LoginView.as_view()),
    path('api/user/account/logout/', LogoutView.as_view()),
    path('api/user/account/register/', RegisterView.as_view()),
    path('api/user/account/refresh_token/', RefreshTokenView.as_view()),
    path('api/user/account/get_user_info/', GetUserInfoView.as_view()),
    #用serve视图处理media文件请求
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    # SPA入口：所有非media/非api的请求指向index
    path('', index),
]
