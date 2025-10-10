from django.http import FileResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscriber, User

from .filters import IngredientFilter, RecipesFilter
from .serializers import (AddRecipeSerializer, FavoriteRecipesSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionsSerializer, TagSerializer)
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )


class UserViewSet(UserViewSet):
    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def self_me(self, request):
        self.get_object = self.get_instance
        return self.retrieve(request)

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = Subscriber.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(pages,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/subscribe')
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(data={'author': author.id,
                                                   'user': request.user.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscription = get_object_or_404(Subscriber,
                                             author=author.id,
                                             user=request.user.id)
            serializer = SubscriptionsSerializer(
                subscription,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscriber.objects.filter(author=author.id,
                                                     user=request.user.id)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': "Подписки не было"},
                            status=status.HTTP_400_BAD_REQUEST)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get',]


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    http_method_names = ['get',]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return AddRecipeSerializer

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shoppingcart = ShoppingCart.objects.filter(user=request.user)
        recipeingredients = (RecipeIngredient.objects.filter(
            recipe=i['recipe_id']).values() for i in shoppingcart.values())
        ingredients = {}
        for recipeingredient in recipeingredients:
            for i in recipeingredient:
                ingredient = Ingredient.objects.get(id=i['ingredients_id'])
                amount = i['amount']
                if ingredient.name not in ingredients:
                    ingredients[ingredient.name] = (
                        ingredient.measurement_unit,
                        amount)
                else:
                    ingredients[ingredient.name] = (
                        ingredient.measurement_unit,
                        ingredients[ingredient.name][1] + amount)
        with open("shopping_cart.txt", "w") as file:
            file.write('Ваш список покупок:' + '\n')
            for ingredient, amount in sorted(ingredients.items(),
                                             key=lambda x: x[0]):
                file.write(f'{ingredient} - {amount[1]}({amount[0]}).' + '\n')
            file.close()
        return FileResponse(open('shopping_cart.txt', 'rb'))

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/shopping_cart')
    def shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        shoppingcart_status = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe).exists()
        if request.method == 'POST':
            if shoppingcart_status:
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if shoppingcart_status:
                ShoppingCart.objects.get(user=request.user,
                                         recipe=recipe).delete()
                return Response('Рецепт удалён из списка покупок!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в списке покупок.'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/favorite')
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favoriterecipes = FavoriteRecipes.objects.filter(
            user=request.user,
            recipe=recipe).exists()
        if request.method == 'POST':
            if favoriterecipes:
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteRecipesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if favoriterecipes:
                FavoriteRecipes.objects.get(user=request.user,
                                            recipe=recipe).delete()
                return Response('Рецепт удалён из списка избранных!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в списке избранных.'},
                            status=status.HTTP_404_NOT_FOUND)
