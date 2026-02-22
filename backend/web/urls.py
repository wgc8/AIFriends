from django.urls import path, re_path

from web.views.index import index
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView
from web.views.user.account.get_user_info import GetUserInfoView

from web.views.user.profile.update import UpdateProfileView

from web.views.create.character.create import CreateCharacterView
urlpatterns = [
    path('api/user/account/login/', LoginView.as_view()),
    path('api/user/account/logout/', LogoutView.as_view()),
    path('api/user/account/register/', RegisterView.as_view()),
    path('api/user/account/refresh_token/', RefreshTokenView.as_view()),
    path('api/user/account/get_user_info/', GetUserInfoView.as_view()),

    path('api/user/profile/update/', UpdateProfileView.as_view()), 
    path('api/create/character/create/', CreateCharacterView.as_view()),
    # SPA入口：所有非media/非api的请求指向index
    path('', index),
    # 兜底路由：所有非media/非static/非assets的请求指向index（注意顺序，必须放在最后）
    re_path(r'^(?!media/|static/|assets/).*$', index)
]
