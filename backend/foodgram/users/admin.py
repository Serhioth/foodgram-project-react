from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'username',
                    'email',
                    'password',
                    'first_name',
                    'last_name',
                    'get_subscribes',
                    'get_shopping_cart',
                    'get_favorited_recipes'
                    )
    list_editable = (
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('username', 'email')
    list_filter = ('last_name', 'email')
    empty_value_display = '-null-'


admin.site.site_title = 'Foddgram admin panel'
admin.site.site_header = 'Foodgram admin panel'

admin.site.register(User, UserAdmin)
