from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction, Payment, Tip
from .serializers import WalletSerializer, TransactionSerializer, PaymentSerializer, TipSerializer
from users.models import User
from studios.models import Studio
from decimal import Decimal

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += Decimal(amount)
        wallet.save()

        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            type='deposit'
        )
        return Response(WalletSerializer(wallet).data)

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        studio_id = request.data.get('studio_id')
        amount = request.data.get('amount')
        service_type = request.data.get('service_type')

        if not all([studio_id, amount, service_type]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        studio = Studio.objects.filter(id=studio_id).first()
        if not studio:
            return Response({'error': 'Studio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        wallet = request.user.wallet
        if wallet.balance < Decimal(amount):
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet.balance -= Decimal(amount)
        wallet.save()
        studio_wallet, _ = Wallet.objects.get_or_create(user=studio.owner)
        studio_wallet.balance += Decimal(amount)
        studio_wallet.save()

        payment = Payment.objects.create(
            studio=studio,
            payer=request.user,
            amount=amount,
            service_type=service_type
        )
        Transaction.objects.create(
            wallet=wallet,
            amount=-Decimal(amount),
            type='payment',
        )
        Transaction.objects.create(
            wallet=studio_wallet,
            amount=Decimal(amount),
            type='payment',
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

class TipView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        amount = request.data.get('amount')
        message = request.data.get('message')

        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        
        wallet = request.user.wallet
        if wallet.balance < Decimal(amount):
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet.balance -= Decimal(amount)
        wallet.save()
        receiver_wallet, _ = Wallet.objects.get_or_create(user=receiver)
        receiver_wallet.balance += Decimal(amount)
        receiver_wallet.save()

        tip = Tip.objects.create(
            sender=request.user,
            receiver=receiver,
            amount=amount,
            message=message
        )
        Transaction.objects.create(
            wallet=wallet,
            amount=-Decimal(amount),
            type='tip',
            tip=tip
        )
        Transaction.objects.create(
            wallet=receiver_wallet,
            amount=Decimal(amount),
            type='tip',
            tip=tip
        )
        return Response(TipSerializer(tip).data)