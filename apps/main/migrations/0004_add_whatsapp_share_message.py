# Migration to add whatsapp_share_message field to Product model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_add_product_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='whatsapp_share_message',
            field=models.TextField(
                blank=True,
                help_text='Custom WhatsApp share message (leave blank for auto-generated)'
            ),
        ),
    ]
