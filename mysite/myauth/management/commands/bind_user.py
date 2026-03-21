from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Выбор первого неадминистративного пользователя
        user = User.objects.filter(is_superuser=False).order_by('pk').first()
        print(f'Updating rules {user!r}...')

        group, created = Group.objects.get_or_create(name='profile_manager')
        permission_profile = Permission.objects.get(codename='view_profile')
        permission_logentry = Permission.objects.get(codename='view_logentry') # Просмотр истории действий в /admin/

        # Добавление разрешения в группу
        group.permissions.add(permission_profile)

        # Присоединение пользователя к группе
        user.groups.add(group)

        # Связать пользователя напрямую с разрешением
        user.user_permissions.add(permission_logentry)

        # Установка флага staff, чтобы пользователь мог войти в /admin/
        user.is_staff = True

        group.save()
        user.save()

        print('Rules updated. User can entry in "/admin".')