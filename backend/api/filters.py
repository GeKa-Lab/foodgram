import django_filters
from django_filters.rest_framework import FilterSet

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilter(FilterSet):
    name = django_filters.rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipesFilter(django_filters.rest_framework.FilterSet):
    author = django_filters.rest_framework.CharFilter(field_name='author')
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = django_filters.filters.NumberFilter(
        method='favorite_recipe')
    is_in_shopping_cart = django_filters.filters.NumberFilter(
        method='recipe_in_shopping_cart')

    def favorite_recipe(self, queryset, name, value):
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def recipe_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
