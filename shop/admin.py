from django.contrib import admin
from .models import Catagory,Product,Cart,Orders,OrderUpdate
# Register your models here.
"""class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','image','description')
 admin.site.register(Catagory,CategoryAdmin)"""
admin.site.register(Catagory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Orders)
admin.site.register(OrderUpdate)