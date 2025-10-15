from django.db import models
from foodgram.settings import (REGEX_AMOUNT, REGEX_SLUG, TEXT_MAX_LENGTH)
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название тега',
        help_text='Укажите название тега'
    )

    slug = models.SlugField(
        null=True,
        unique=True,
        validators=[REGEX_SLUG],
        verbose_name='Аббревиатура тега',
        help_text='Укажите аббревиатуру тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        unique=True,
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название ингредиента',
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Единицы измерения',
        help_text='Укажите единицы измерения'
    )

    class Meta:
        ordering = ('id', 'name')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Тег рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингридиент рецепта',
    )
    is_favorited = models.BooleanField(
        default=True,
        verbose_name='Находится в избранном',
        help_text='Отметьте рецепт в избранное'
    )
    is_in_shopping_cart = models.BooleanField(
        default=True,
        verbose_name='Находится в корзине',
        help_text='Отложите рецепт в корзину'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        help_text='Укажите изображение рецепта',
        upload_to='recipes_images'
    )
    name = models.CharField(
        max_length=TEXT_MAX_LENGTH,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Укажите описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[REGEX_AMOUNT],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления, от 1 мин'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipetags',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipetags',
        verbose_name='Тег рецепта',
        help_text='Укажите тег рецепта'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Тег - рецепта'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'tags'],
            name='unique_recipe_tags'
        )]

    def __str__(self):
        return f"{self.recipe} - {self.tags}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент рецепта',
        help_text='Укажите ингредиент рецепта'
    )
    amount = models.PositiveIntegerField(
        validators=[REGEX_AMOUNT],
        verbose_name='Кол-во ингредиента',
        help_text='Укажите кол-во ингредиента, от 1 и более'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент - рецепта'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredients'],
            name='unique_recipe_ingredients'
        )]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredients} - {self.amount} '
                f'{self.ingredients.measurement_unit}')


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='пользователь',
        help_text='Укажите пользователя'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Рецепт - пользователь'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_user'
        )]

    def __str__(self):
        return f"{self.recipe} - {self.user}"


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='пользователь',
        help_text='Укажите пользователя'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_shoppingcart'
        )]

    def __str__(self):
        return f"{self.recipe} - {self.user}"
