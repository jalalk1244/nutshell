import uuid
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion

def prepare_existing(apps, schema_editor):
    Order = apps.get_model('checkout', 'Order')
    Line = apps.get_model('checkout', 'OrderLineItem')
    alias = schema_editor.connection.alias
    orders = Order.objects.using(alias)
    for field in ('order_number', 'stripe_pid'):
        duplicates = orders.exclude(**{field: ''}).values(field).annotate(n=models.Count('id')).filter(n__gt=1)
        if duplicates.exists():
            raise RuntimeError('Existing duplicate order references/payment intents need manual reconciliation before migration. No records were deleted.')
    if Line.objects.using(alias).filter(models.Q(quantity__lt=1) | models.Q(quantity__gt=99)).exists():
        raise RuntimeError('Existing invalid line quantities need manual reconciliation before migration. No records were deleted.')
    for order in orders.iterator():
        order.checkout_key = uuid.uuid4()
        order.save(update_fields=['checkout_key'])
    for line in Line.objects.using(alias).all().iterator():
        line.unit_price = (line.lineitem_total / Decimal(line.quantity)).quantize(Decimal('0.01'))
        line.save(update_fields=['unit_price'])

class Migration(migrations.Migration):
    dependencies = [('checkout', '0002_order_user_profile')]
    operations = [
        migrations.AddField(model_name='order', name='checkout_key', field=models.UUIDField(null=True, editable=False)),
        migrations.AddField(model_name='order', name='payment_status', field=models.CharField(max_length=12, default='legacy', choices=[('legacy', 'Unverified legacy order'), ('pending', 'Awaiting payment'), ('failed', 'Payment failed'), ('paid', 'Paid')])),
        migrations.AddField(model_name='order', name='currency', field=models.CharField(max_length=3, default='usd')),
        migrations.AddField(model_name='orderlineitem', name='unit_price', field=models.DecimalField(max_digits=6, decimal_places=2, null=True, editable=False)),
        migrations.AlterField(model_name='orderlineitem', name='lineitem_total', field=models.DecimalField(max_digits=10, decimal_places=2, editable=False)),
        migrations.AlterField(model_name='orderlineitem', name='quantity', field=models.IntegerField(default=1)),
        migrations.AlterField(model_name='orderlineitem', name='product', field=models.ForeignKey(to='products.product', on_delete=django.db.models.deletion.PROTECT)),
        migrations.RunPython(prepare_existing, migrations.RunPython.noop),
        migrations.AlterField(model_name='order', name='checkout_key', field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
        migrations.AlterField(model_name='order', name='order_number', field=models.CharField(max_length=32, editable=False, unique=True)),
        migrations.AddConstraint(model_name='order', constraint=models.UniqueConstraint(fields=['stripe_pid'], condition=~models.Q(stripe_pid=''), name='unique_nonempty_payment_intent')),
        migrations.AddConstraint(model_name='orderlineitem', constraint=models.CheckConstraint(condition=models.Q(quantity__gte=1, quantity__lte=99), name='order_quantity_1_to_99')),
        migrations.CreateModel(name='PaymentEvent', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('event_id', models.CharField(max_length=255, unique=True)),
            ('event_type', models.CharField(max_length=80)),
            ('received_at', models.DateTimeField(auto_now_add=True)),
            ('order', models.ForeignKey(to='checkout.order', on_delete=django.db.models.deletion.PROTECT)),
        ]),
    ]
