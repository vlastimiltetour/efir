from django.core.management.base import BaseCommand
from catalog.ml import get_data

class Command(BaseCommand):
    help = 'Trénování modelů'

    def handle(self, *args, **options):
        print("Training started!")
        print(get_data.get_similarity_matrix())

        print(get_data.get_recommendations(48))
        print("Training finished!")

