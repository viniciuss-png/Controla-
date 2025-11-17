from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TransacaoViewSet, CategoriaViewSet, ContaViewSet,UserRegisterView, MetaFinanceiraViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()

router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'metas', MetaFinanceiraViewSet, basename='meta')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', UserRegisterView.as_view(), name='user_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]