from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0003_tablerestaurant_nombre_clients_actuels'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablerestaurant',
            name='qr_token',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='Token QR Code'),
        ),
        migrations.AddField(
            model_name='tablerestaurant',
            name='qr_status',
            field=models.CharField(
                choices=[('active', 'Active'), ('inactive', 'Inactive'), ('blocked', 'Bloquée')],
                default='inactive',
                max_length=10,
                verbose_name='Statut QR Code',
            ),
        ),
        migrations.AddField(
            model_name='tablerestaurant',
            name='last_login_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Dernière connexion'),
        ),
        migrations.AddField(
            model_name='tablerestaurant',
            name='last_login_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='Dernière IP de connexion'),
        ),
    ]
