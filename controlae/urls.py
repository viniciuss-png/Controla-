from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TransacaoViewSet, CategoriaViewSet, ContaViewSet

router = DefaultRouter()

router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'contas', ContaViewSet, basename='conta')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]