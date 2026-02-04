# Final sync migration - mark current model state as synchronized
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0009_fix_final_state'),
    ]

    operations = [
        # Migration vide pour marquer que le modèle est synchronisé
        migrations.RunSQL(
            sql="SELECT 1",
            reverse_sql="SELECT 1"
        ),
    ]
