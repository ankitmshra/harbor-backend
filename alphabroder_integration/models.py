from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    # Category
    category = models.CharField(max_length=255, unique=True, primary_key=True)

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.category


class Style(models.Model):
    style_number = models.CharField(max_length=255, unique=True, primary_key=True)
    short_description = models.CharField(max_length=255)
    mill_number = models.CharField(max_length=255)
    mill_name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='styles',
    )
    markup_code = models.CharField(max_length=255)
    full_feature_description = models.TextField()

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Style")
        verbose_name_plural = _("Styles")

    def __str__(self):
        return f"{self.style_number} - {self.short_description}"


class Products(models.Model):
    is_new = models.BooleanField(default=False)
    item_number = models.CharField(max_length=255, unique=True, primary_key=True)
    style_number = models.ForeignKey(
        Style,
        on_delete=models.CASCADE,
        related_name='products',
    )
    color_name = models.CharField(max_length=255)
    color_group_code = models.CharField(max_length=255)
    color_code = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=255)
    size_group = models.CharField(max_length=255)
    size_code = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    case_qty = models.IntegerField()
    weight = models.CharField(max_length=255)
    front_image = models.CharField(max_length=255)
    back_image = models.CharField(max_length=255)
    side_image = models.CharField(max_length=255)
    gtin = models.CharField(max_length=255)
    launch_date = models.IntegerField()
    pms_color = models.CharField(max_length=255)
    size_sort_order = models.IntegerField()
    mktg_color_number = models.IntegerField()
    mktg_color_name = models.CharField(max_length=255)
    mktg_color_hex_code = models.CharField(max_length=255)

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.item_number


class Inventory(models.Model):
    item_number = models.OneToOneField(
        Products,
        on_delete=models.CASCADE,
        related_name='inventory',
        primary_key=True,
    )
    gtin_number = models.CharField(max_length=255, unique=True)
    mill_style_number = models.CharField(max_length=255)
    cc = models.IntegerField(default=0)
    cn = models.IntegerField(default=0)
    fo = models.IntegerField(default=0)
    gd = models.IntegerField(default=0)
    kc = models.IntegerField(default=0)
    ma = models.IntegerField(default=0)
    ph = models.IntegerField(default=0)
    td = models.IntegerField(default=0)
    pz = models.IntegerField(default=0)
    bz = models.IntegerField(default=0)
    fz = models.IntegerField(default=0)
    px = models.IntegerField(default=0)
    fx = models.IntegerField(default=0)
    bx = models.IntegerField(default=0)
    gx = models.IntegerField(default=0)
    drop_ship = models.IntegerField(default=0)

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.item_number}"
    

class Price(models.Model):
    item_number = models.OneToOneField(
        Products,
        on_delete=models.CASCADE,
        related_name='price',
        primary_key=True,
    )
    gtin_number = models.CharField(max_length=255, unique=True)
    price_per_piece = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_per_dozen = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_per_case = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.item_number}"

