from django.db import migrations


def create_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Create groups
    normal_user_group, _ = Group.objects.get_or_create(name='Normal User')
    restaurant_user_group, _ = Group.objects.get_or_create(name='Restaurant User')

    # Assign permissions to normal user group
    normal_user_permissions = [
        'add_review', 'change_review', 'delete_review',  # Assuming these are the review permissions
    ]
    for perm_code in normal_user_permissions:
        perm = Permission.objects.get(codename=perm_code)
        normal_user_group.permissions.add(perm)

    # Assign permissions to restaurant user group
    restaurant_user_permissions = [
        'add_restaurant', 'change_restaurant', 'delete_restaurant',
        'add_meal', 'change_meal', 'delete_meal',  # Assuming these are the meal permissions
    ]
    for perm_code in restaurant_user_permissions:
        perm = Permission.objects.get(codename=perm_code)
        restaurant_user_group.permissions.add(perm)


def remove_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Normal User', 'Restaurant User']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('customusers', '0002_alter_myuser_username'),
    ]

    operations = [
        migrations.RunPython(create_user_groups, remove_user_groups),
    ]