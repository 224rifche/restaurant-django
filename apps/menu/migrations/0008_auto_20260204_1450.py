# Generated migration to mark current state as synchronized
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0007_cleanup_categorie_field'),
    ]

    operations = [
        # Migration vide - le modèle est déjà synchronisé avec la base de données
        migrations.RunSQL(
            sql="SELECT 1",  # SQL neutre pour marquer comme appliquée
            reverse_sql="SELECT 1"
        ),
    ]
