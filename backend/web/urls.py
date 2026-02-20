from django.urls import path
from django.conf import settings
from django.views.static import serve  # 处理静态/媒体文件的核心视图
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from web.views.index import index

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #用serve视图处理media文件请求
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    # SPA入口：所有非media/非api的请求指向index
    path('', index),
]
