from django.db import migrations, models

def check_duplicates(apps, schema_editor):
    WishList = apps.get_model('products', 'WishList')
    duplicates = WishList.objects.using(schema_editor.connection.alias).values('user', 'wished_product').annotate(n=models.Count('id')).filter(n__gt=1)
    if duplicates.exists():
        raise RuntimeError('Duplicate wishlist entries require manual reconciliation before migration. No records were deleted.')

class Migration(migrations.Migration):
    dependencies = [('products', '0007_alter_productrating_product')]
    operations = [migrations.RunPython(check_duplicates, migrations.RunPython.noop),
        migrations.AddConstraint(model_name='wishlist', constraint=models.UniqueConstraint(fields=['user', 'wished_product'], name='unique_wishlist_product'))]
