# Generated by Django 4.0.4 on 2024-01-01 03:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('category_image', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('product_id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='Product ID')),
                ('product_number', models.CharField(max_length=255, unique=True)),
                ('brand_name', models.CharField(max_length=255)),
                ('short_description', models.CharField(max_length=255)),
                ('full_feature_description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Variations',
            fields=[
                ('variation_id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='Variation ID')),
                ('item_number', models.CharField(max_length=255, unique=True)),
                ('color_name', models.CharField(max_length=255)),
                ('hex_code', models.CharField(max_length=255)),
                ('size', models.CharField(max_length=255)),
                ('case_qty', models.IntegerField()),
                ('weight', models.CharField(max_length=255)),
                ('front_image', models.CharField(max_length=255)),
                ('back_image', models.CharField(max_length=255)),
                ('side_image', models.CharField(max_length=255)),
                ('gtin', models.CharField(max_length=255)),
                ('quantity', models.IntegerField(null=True)),
                ('price_per_piece', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('price_per_dozen', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('price_per_case', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variations', to='products.products')),
            ],
            options={
                'verbose_name': 'Variation',
                'verbose_name_plural': 'Variations',
                'ordering': ('-created_at',),
            },
        ),
    ]
