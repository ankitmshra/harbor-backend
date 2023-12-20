from django.db import models


class AlphaBroderProductsStyle(models.Model):
    # Style
    style = models.CharField(max_length=255, unique=True, primary_key=True)

    # Style Name
    style_name = models.CharField(max_length=255)

    # Category
    category = models.CharField(max_length=255)

    # Subcategory
    subcategory = models.CharField(max_length=255)

    # Thumbnail Name
    thumbnail_name = models.CharField(max_length=255)

    # Normal Image Name
    normal_image_name = models.CharField(max_length=255)

    # Full Feature Description
    full_feature_description = models.TextField()

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.style


class AlphaBroderProducts(models.Model):
    # Item Status
    item_status = models.CharField(max_length=255, blank=True, null=True)

    # SKU
    sku = models.CharField(max_length=255, unique=True, primary_key=True)

    # Style
    style = models.ForeignKey(
        AlphaBroderProductsStyle,
        on_delete=models.CASCADE,
    )

    # Short Description
    short_description = models.CharField(max_length=255)

    # Color Group
    color_group = models.CharField(max_length=255)

    # Color Code
    color_code = models.CharField(max_length=255)

    # Color
    color = models.CharField(max_length=255)

    # Hex Code
    hex_code = models.CharField(max_length=255)

    # Size Group
    size_group = models.CharField(max_length=255)

    # Size Code
    size_code = models.CharField(max_length=255)

    # Size
    size = models.CharField(max_length=255)

    # Case Qty
    case_qty = models.IntegerField()

    # Weight
    weight = models.CharField(max_length=255)

    # Mill #
    mill_number = models.CharField(max_length=255)

    # Mill Name
    mill_name = models.CharField(max_length=255)

    # Category
    category = models.CharField(max_length=255)

    # Subcategory
    subcategory = models.CharField(max_length=255)

    # Piece
    piece = models.DecimalField(max_digits=10,
                                      decimal_places=2, blank=True, null=True)

    # Dozen
    dozen = models.DecimalField(max_digits=10,
                                      decimal_places=2, blank=True, null=True)

    # Case
    case = models.DecimalField(max_digits=10,
                                     decimal_places=2, blank=True, null=True)

    # Closeout Price
    closeout_price = models.DecimalField(max_digits=10,
                                         decimal_places=2,
                                         blank=True, null=True)

    # Start Date
    start_date = models.DateField()

    # End Date
    end_date = models.DateField()

    # Thumbnail Name
    thumbnail_name = models.CharField(max_length=255)

    # Normal Image Name
    normal_image_name = models.CharField(max_length=255)

    # Full Feature Description
    full_feature_description = models.TextField()

    # Gtin
    gtin = models.CharField(max_length=255)

    # Image Fields
    side_image = models.CharField(max_length=255)
    back_image = models.CharField(max_length=255)

    # product create and update fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.short_description


class Inventory(models.Model):
    item_number = models.CharField(max_length=255, unique=True,
                                   primary_key=True)
    gtin_number = models.CharField(max_length=255, unique=True)
    mill_code = models.CharField(max_length=255)
    mill_description = models.CharField(max_length=255)
    style_number = models.ForeignKey(
        AlphaBroderProductsStyle,
        on_delete=models.CASCADE,
    )
    mill_style_number = models.CharField(max_length=255)
    style_name = models.CharField(max_length=255)
    color_code = models.CharField(max_length=255)
    color_description = models.CharField(max_length=255)
    size_code = models.CharField(max_length=255)
    size_description = models.CharField(max_length=255)
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
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

    def update_alpha_broder_style(self):
        alpha_broder_style = self.style_number
        if alpha_broder_style:
            alpha_broder_style.style_name = self.style_name
            alpha_broder_style.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_alpha_broder_style()

    def __str__(self):
        return f"{self.item_number} - {self.style_name}"
