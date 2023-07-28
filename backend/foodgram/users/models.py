from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user-model class"""

    is_subscribed = models.BooleanField(default=False)
    subscribes = models.ManyToManyField('self', blank=True, symmetrical=False)

    email = models.EmailField(
        'Почта',
        unique=True,
        max_length=254,
        help_text='Почта пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_subscribes(self):
        return (
            [subscription.username for subscription in self.subscribes.all()]
        )

    def get_shopping_cart(self):
        return [recipe.name for recipe in self.shopping_cart.all()]

    def get_favorited_recipes(self):
        return [recipe.name for recipe in self.favorited_recipes.all()]

    def __str__(self) -> str:
        return self.username
