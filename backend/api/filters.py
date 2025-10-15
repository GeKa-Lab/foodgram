from django_filters import rest_framework
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientsFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author')
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = rest_framework.NumberFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
