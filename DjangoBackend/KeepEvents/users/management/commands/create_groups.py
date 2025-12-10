from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create base groups: Admin, IMG Member, Public."

    def handle(self, *args, **options):
        group_names = ["Admin", "IMG Member", "Public"]

        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
            else:
                self.stdout.write(f"Group already exists: {name}")

        self.stdout.write(self.style.SUCCESS("Done creating base groups."))
