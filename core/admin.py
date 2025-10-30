from django.contrib import admin
from .models import Categoria, Conta, Transacao 
from django.contrib.auth.models import User  

class UserOwnedModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

@admin.register(Categoria)
class CategoriaAdmin(UserOwnedModelAdmin):
    list_display = ('nome', 'tipo_categoria', 'usuario')
    list_filter = ('tipo_categoria',)

@admin.register(Conta)
class ContaAdmin(UserOwnedModelAdmin):
    list_display = ('nome', 'saldo_inicial', 'usuario')

@admin.register(Transacao)
class TransacaoAdmin(UserOwnedModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'tipo', 'pago', 'categoria', 'conta', 'parcelas')
    list_editable = ('pago',)
    list_filter = ('tipo', 'pago', 'categoria', 'conta', 'data')
    search_fields = ('descricao',)
    ordering = ('-data',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            kwargs["queryset"] = Categoria.objects.filter(usuario=request.user)
        if db_field.name == "conta":
            kwargs["queryset"] = Conta.objects.filter(usuario=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)