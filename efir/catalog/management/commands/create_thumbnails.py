from catalog.models import Photo

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps


THUMBNAIL_SIZE = 500
THUMBNAIL_QUALITY = 82

class Command(BaseCommand):
    help = 'Creates photo miniatures'

    def add_arguments(self, parser):
        parser.add_argument('-l', '--limit', type=int, help='Number of operations')

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0
        errors = 0    

        limit = kwargs.get("limit")

        photos = Photo.objects.exclude(photo="")

        if limit is not None:
            photos = photos[:limit] # then the database itself limits the results. Django won't fetch all photos and then discard the rest.

        for photo in photos.iterator(chunk_size=100): # limits db - loads x rows from database, not pictures
            print('photo', photo)


            original_name = photo.photo.name
            thumbnail_name = photo.thumbnail_name

            print('original_name: ', original_name, "thubmanil_name: ", thumbnail_name)

            if photo.photo.storage.exists(thumbnail_name): #checking the path
                print('checking thumbnail name')
                skipped += 1
                continue

            try:
                img = Image.open(self.photo)
                img.verify()
                # reopen because img.verify() moves pointer to the end of the file
                img = Image.open(self.photo)

                # convert png to RGB
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Calculate new dimensions to maintain aspect ratio with a width of 800
                new_width = 800
                original_width, original_height = img.size
                new_height = int((new_width / original_width) * original_height)

                # Resize the image
                img = img.resize((new_width, new_height), Image.LANCZOS)

                # Prepare the image for saving
                temp_img = BytesIO()
                # Save the image as JPEG
                img.save(temp_img, format="JPEG", quality=70, optimize=True)
                temp_img.seek(0)

                # Change file extension to .jpg
                original_name, _ = self.photo.name.lower().split(".")
                img = f"{original_name}.jpg"

                # Save the BytesIO object to the ImageField with the new filename
                self.photo.save(img, ContentFile(temp_img.read()), save=False)
            
            except (IOError, SyntaxError, Exception()) as e:
            
                errors += 1

                self.stderr.write(
                    self.style.ERROR(
                        f"ERROR: {original_name}: {e}"
                    )
                )


        self.stdout.write("")
        self.stdout.write(
        self.style.SUCCESS(
            f"Finished. "
            f"Created: {created}, "
            f"Skipped: {skipped}, "
            f"Errors: {errors}"
        )
    )