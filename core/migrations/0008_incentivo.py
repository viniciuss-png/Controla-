"""Generated migration for Incentivo model."""
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_lembrete_notificacao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Incentivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('conclusao', 'Incentivo Conclusão'), ('enem', 'Incentivo ENEM')], max_length=20)),
                ('ano', models.IntegerField(blank=True, null=True)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('liberado', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.conta')),
                ('transacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.transacao')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-criado_em'],
                'verbose_name': 'Incentivo',
                'verbose_name_plural': 'Incentivos',
            },
        ),
    ]
