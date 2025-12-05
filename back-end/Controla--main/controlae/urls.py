from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TransacaoViewSet, CategoriaViewSet, ContaViewSet, UserRegisterView, MetaFinanceiraViewSet, LembreteViewSet, NotificacaoViewSet
from core.views import IncentivoConclusaoCreateView, IncentivoConclusaoLiberarView, IncentivoEnemCreateView
from core.views import RelatorioFinanceiroPDFView, DashboardDataView
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
router.register(r'lembretes', LembreteViewSet, basename='lembrete')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', UserRegisterView.as_view(), name='user_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/incentivos/conclusao/', IncentivoConclusaoCreateView.as_view(), name='incentivo_conclusao_create'),
    path('api/incentivos/conclusao/liberar/', IncentivoConclusaoLiberarView.as_view(), name='incentivo_conclusao_liberar'),
    path('api/incentivos/enem/', IncentivoEnemCreateView.as_view(), name='incentivo_enem_create'),
    path('api/relatorio/pdf/', RelatorioFinanceiroPDFView.as_view(), name='relatorio_pdf'),
    path('api/dashboard/', DashboardDataView.as_view(), name='dashboard_data'),
]