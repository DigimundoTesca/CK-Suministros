from rest_framework import serializers
from django.utils import timezone

from orders.models import CustomerOrderDetail, CustomerOrder
from products.models import Cartridge, PackageCartridgeRecipe, PackageCartridge
from users.models import User as UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'email',)


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=UserProfile.objects.all(), source='user')

    class Meta:
        model = UserProfile
        fields = ('user', 'user_id', 'phone_number',)


class CartridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartridge
        fields = ('id', 'name', 'price', 'category', 'image')


class PackageCartridgeRecipeSerializer(serializers.ModelSerializer):
    cartridge = CartridgeSerializer(read_only=True)

    class Meta:
        model = PackageCartridgeRecipe
        fields = ('id', 'cartridge', 'quantity',)


class PackageCartridgeSerializer(serializers.ModelSerializer):
    package_cartridge_recipe = PackageCartridgeRecipeSerializer(many=True, read_only=True,
                                                                source='packagecartridgerecipe_set')

    class Meta:
        model = PackageCartridge
        fields = ('id', 'name', 'price', 'package_cartridge_recipe',)


class CustomerOrderDetailSerializer(serializers.ModelSerializer):
    cartridge = CartridgeSerializer(read_only=True, )
    package_cartridge = PackageCartridgeSerializer(read_only=True, )

    class Meta:
        model = CustomerOrderDetail
        fields = ('id', 'cartridge', 'package_cartridge', 'quantity',)


class DateTimeFieldWihTZ(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


class CustomerOrderSerializer(serializers.ModelSerializer):
    customer_order_details = CustomerOrderDetailSerializer(many=True, read_only=True, source='customerorderdetail_set')
    customer_user = UserProfileSerializer(read_only=True, )
    customer_user_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=UserProfile.objects.all(),
                                                          source='customer_user')
    delivery_date = DateTimeFieldWihTZ()
    created_at = DateTimeFieldWihTZ()

    class Meta:
        model = CustomerOrder
        fields = (
            'id', 'created_at', 'delivery_date', 'customer_user', 'customer_user_id', 'customer_order_details',
            'status', 'price',
            'latitude', 'longitude', 'score', 'pin')


class CustomerOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = ('status',)


class CustomerOrderScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = ('score',)


class CustomerOrderPinSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = ('pin',)