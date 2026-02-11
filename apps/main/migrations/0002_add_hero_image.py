# Migration to add missing hero_image field to CompanyInfo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='hero_image',
            field=models.ImageField(blank=True, upload_to='company/hero/'),
        ),
    ]
