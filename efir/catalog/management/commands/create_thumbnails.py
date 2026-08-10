from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates photo miniatures'

    def add_arguments(self, parser):
        parser.add_argument('-l', '--limit', type=int, help='Number of operations')

    def handle(self, *args, **kwargs):
        processed = 0
        skipped = 0
        failed = 0        

    self.stdout.write("")
    self.stdout.write(
    self.style.SUCCESS(
        f"Finished. "
        f"Created: {created}, "
        f"Skipped: {skipped}, "
        f"Errors: {errors}"
    )
)