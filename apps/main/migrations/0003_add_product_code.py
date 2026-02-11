# Generated migration for product_code field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_add_hero_image'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(blank=True, help_text='Your physical product code (e.g., EYE-PHO-042, SKU-12345)', max_length=50, null=True, unique=True),
        ),
    ]
