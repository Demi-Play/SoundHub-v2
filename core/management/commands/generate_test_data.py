from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import UserProfile
from studios.models import Studio, StudioVerification, StudioStatistics
from chats.models import Project
from ratings.models import Rating
from payments.models import Wallet, Payment
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates test data for the application'

    def handle(self, *args, **kwargs):
        # Создаем пользователей
        self.create_users()
        # Создаем студии
        self.create_studios()
        # Создаем проекты
        self.create_projects()
        # Создаем рейтинги
        self.create_ratings()
        # Создаем платежи
        self.create_payments()

    def create_users(self):
        # Создаем владельцев студий
        for i in range(10):
            user = User.objects.create_user(
                username=f'studio_owner{i+1}',
                email=f'owner{i+1}@soundhub.com',
                password='testpass123',
                first_name=f'Owner{i+1}',
                last_name=f'Studio{i+1}',
                user_type='studio_owner',
                is_verified=True
            )
            UserProfile.objects.create(
                user=user,
                bio=f'Professional studio owner with {random.randint(5, 20)} years of experience',
                social_links={'instagram': f'@studio_owner{i+1}', 'facebook': f'studio_owner{i+1}'}
            )
            Wallet.objects.create(user=user, balance=random.randint(1000, 10000))

        # Создаем музыкантов
        for i in range(20):
            user = User.objects.create_user(
                username=f'musician{i+1}',
                email=f'musician{i+1}@soundhub.com',
                password='testpass123',
                first_name=f'Musician{i+1}',
                last_name=f'Artist{i+1}',
                user_type='musician',
                is_verified=True
            )
            UserProfile.objects.create(
                user=user,
                bio=f'Professional musician specializing in {random.choice(["rock", "jazz", "classical", "pop"])}',
                social_links={'instagram': f'@musician{i+1}', 'facebook': f'musician{i+1}'},
                instruments=random.sample(['guitar', 'piano', 'drums', 'bass', 'vocals'], random.randint(1, 3)),
                genres=random.sample(['rock', 'jazz', 'classical', 'pop', 'blues'], random.randint(1, 3))
            )
            Wallet.objects.create(user=user, balance=random.randint(500, 5000))

    def create_studios(self):
        owners = User.objects.filter(user_type='studio_owner')
        for i, owner in enumerate(owners):
            studio = Studio.objects.create(
                name=f'Studio {i+1}',
                owner=owner,
                description=f'Professional recording studio {i+1} with state-of-the-art equipment',
                address=f'{random.randint(1, 100)} Music Street, City',
                equipment_list=random.sample(['Neumann U87', 'SSL Console', 'Pro Tools HD', 'Genelec Monitors', 'API Preamps'], 3),
                pricing={'recording': random.randint(50, 200), 'mixing': random.randint(100, 300), 'mastering': random.randint(150, 400)},
                commission_percent=random.randint(5, 15)
            )
            StudioVerification.objects.create(
                user=owner,
                status='approved'
            )
            StudioStatistics.objects.create(
                studio=studio,
                total_projects=random.randint(5, 20),
                completed_projects=random.randint(3, 15),
                total_revenue=random.randint(1000, 10000),
                average_rating=random.uniform(3.5, 5.0),
                last_updated=timezone.now()
            )

    def create_projects(self):
        studios = Studio.objects.all()
        musicians = User.objects.filter(user_type='musician')
        statuses = ['new', 'in_progress', 'completed', 'cancelled']
        
        for i in range(15):
            studio = random.choice(studios)
            client = random.choice(musicians)
            status = random.choice(statuses)
            created_at = timezone.now() - timedelta(days=random.randint(1, 30))
            
            project = Project.objects.create(
                title=f'Project {i+1}',
                description=f'Music project {i+1} for {client.get_full_name()}',
                client=client,
                studio=studio,
                status=status,
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(1, 10))
            )

    def create_ratings(self):
        projects = Project.objects.filter(status='completed')
        for project in projects:
            Rating.objects.create(
                project=project,
                rated_by=project.client,
                score=random.randint(3, 5),
                comment=f'Great experience working with {project.studio.name}',
                created_at=project.updated_at
            )

    def create_payments(self):
        projects = Project.objects.filter(status='completed')
        for project in projects:
            Payment.objects.create(
                studio=project.studio,
                payer=project.client,
                amount=random.randint(500, 2000),
                service_type=random.choice(['recording', 'mixing', 'mastering']),
                is_processed=True
            ) 