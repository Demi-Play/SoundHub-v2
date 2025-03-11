from rest_framework import serializers
from .models import Wallet, Transaction, Payment, Tip
from users.serializers import UserSerializer
from studios.serializers import StudioSerializer

class WalletSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = ['user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'type', 'created_at', 'payment', 'tip']

class PaymentSerializer(serializers.ModelSerializer):
    studio = StudioSerializer(read_only=True)
    payer = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'studio', 'payer', 'amount', 'service_type', 'is_processed']

class TipSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Tip
        fields = ['id', 'sender', 'receiver', 'amount', 'message', 'created_at']