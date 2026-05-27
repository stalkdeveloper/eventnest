from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['account_type'], name='accounts_user_account_type_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['is_verified'], name='accounts_user_is_verified_idx'),
        ),
        # email is already unique (has implicit index) — skip
    ]
