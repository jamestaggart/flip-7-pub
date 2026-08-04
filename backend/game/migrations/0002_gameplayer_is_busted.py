from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='is_busted',
            field=models.BooleanField(default=False),
        ),
    ]
