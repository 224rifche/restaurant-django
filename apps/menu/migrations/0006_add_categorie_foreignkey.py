# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_categories_plats'),
    ]

    operations = [
        migrations.AddField(
            model_name='plat',
            name='categorie_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='menu.categorieplat',
                verbose_name='Catégorie'
            ),
        ),
    ]
