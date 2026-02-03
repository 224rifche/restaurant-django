# Migration vide pour marquer l'état comme synchronisé
# Le modèle est déjà correct, pas besoin de modifications
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_add_categorie_foreignkey'),
    ]

    operations = [
        # Aucune opération nécessaire - le modèle est déjà synchronisé
        migrations.RunSQL(
            sql="SELECT 1",  # SQL neutre
            reverse_sql="SELECT 1"
        ),
    ]
