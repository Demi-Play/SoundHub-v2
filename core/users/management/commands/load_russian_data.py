from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile
from studios.models import Studio, StudioVerification, StudioStatistics
from chats.models import Project
from ratings.models import Rating
from payments.models import Wallet, Payment
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Load Russian test data into the database'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 1. Create or get Users
                studio_owner, created = User.objects.get_or_create(
                    username="ivan_studio",
                    defaults={
                        "email": "ivan@soundhub.com",
                        "first_name": "Иван",
                        "last_name": "Петров",
                        "user_type": "studio_owner",
                        "is_verified": True
                    }
                )
                if created:
                    studio_owner.set_password("testpass123")
                    studio_owner.save()
                    self.stdout.write('Created studio owner user')
                else:
                    self.stdout.write('Studio owner user already exists')

                musician, created = User.objects.get_or_create(
                    username="maria_music",
                    defaults={
                        "email": "maria@soundhub.com",
                        "first_name": "Мария",
                        "last_name": "Смирнова",
                        "user_type": "musician",
                        "is_verified": True
                    }
                )
                if created:
                    musician.set_password("testpass123")
                    musician.save()
                    self.stdout.write('Created musician user')
                else:
                    self.stdout.write('Musician user already exists')

                # 2. Create User Profiles if they don't exist
                studio_owner_profile, created = UserProfile.objects.get_or_create(
                    user=studio_owner,
                    defaults={
                        "bio": "Профессиональная студия звукозаписи",
                        "social_links": {"instagram": "@ivan_studio", "facebook": "ivan_studio"},
                        "instruments": [],
                        "genres": []
                    }
                )
                if created:
                    self.stdout.write('Created studio owner profile')
                else:
                    self.stdout.write('Studio owner profile already exists')

                musician_profile, created = UserProfile.objects.get_or_create(
                    user=musician,
                    defaults={
                        "bio": "Вокалистка и композитор",
                        "social_links": {"instagram": "@maria_music", "facebook": "maria_music"},
                        "instruments": ["фортепиано", "гитара"],
                        "genres": ["поп", "джаз"]
                    }
                )
                if created:
                    self.stdout.write('Created musician profile')
                else:
                    self.stdout.write('Musician profile already exists')

                # 3. Create Studio and related objects if they don't exist
                studio, created = Studio.objects.get_or_create(
                    owner=studio_owner,
                    defaults={
                        "name": "ЗвукоМастер",
                        "description": "Современная студия звукозаписи с профессиональным оборудованием",
                        "address": "ул. Звукозаписи, 42, Москва",
                        "equipment_list": ["Neumann U87", "SSL 4000", "Pro Tools HD"],
                        "pricing": {"recording": 5000, "mixing": 8000, "mastering": 10000},
                        "commission_percent": 10.00
                    }
                )
                if created:
                    self.stdout.write('Created studio')
                else:
                    self.stdout.write('Studio already exists')

                verification, created = StudioVerification.objects.get_or_create(
                    user=studio_owner,
                    defaults={"status": "approved"}
                )
                if created:
                    self.stdout.write('Created studio verification')
                else:
                    self.stdout.write('Studio verification already exists')

                stats, created = StudioStatistics.objects.get_or_create(
                    studio=studio,
                    defaults={
                        "total_projects": 25,
                        "completed_projects": 20,
                        "total_revenue": 500000.00,
                        "average_rating": 4.8
                    }
                )
                if created:
                    self.stdout.write('Created studio statistics')
                else:
                    self.stdout.write('Studio statistics already exists')

                # 4. Create Project if it doesn't exist
                project, created = Project.objects.get_or_create(
                    title="Альбом 'Новые Горизонты'",
                    defaults={
                        "description": "Запись и сведение дебютного альбома",
                        "client": musician,
                        "studio": studio,
                        "status": "completed"
                    }
                )
                if created:
                    self.stdout.write('Created project')
                else:
                    self.stdout.write('Project already exists')

                # 5. Create Rating if it doesn't exist
                rating, created = Rating.objects.get_or_create(
                    project=project,
                    rated_by=musician,
                    defaults={
                        "score": 5,
                        "comment": "Отличная студия, профессиональное оборудование и специалисты"
                    }
                )
                if created:
                    self.stdout.write('Created rating')
                else:
                    self.stdout.write('Rating already exists')

                # 6. Create Wallets if they don't exist
                studio_owner_wallet, created = Wallet.objects.get_or_create(
                    user=studio_owner,
                    defaults={"balance": 50000.00}
                )
                if created:
                    self.stdout.write('Created studio owner wallet')
                else:
                    self.stdout.write('Studio owner wallet already exists')

                musician_wallet, created = Wallet.objects.get_or_create(
                    user=musician,
                    defaults={"balance": 25000.00}
                )
                if created:
                    self.stdout.write('Created musician wallet')
                else:
                    self.stdout.write('Musician wallet already exists')

                # 7. Create Payment if it doesn't exist
                payment, created = Payment.objects.get_or_create(
                    studio=studio,
                    payer=musician,
                    defaults={
                        "amount": 15000.00,
                        "service_type": "recording",
                        "is_processed": True
                    }
                )
                if created:
                    self.stdout.write('Created payment')
                else:
                    self.stdout.write('Payment already exists')

                self.stdout.write(self.style.SUCCESS('Successfully processed Russian test data'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            raise 