from catalog.models import Photo

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps


THUMBNAIL_SIZE = 800
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
            storage = photo.photo.storage

            print('original_name: ', original_name, "thubmanil_name: ", thumbnail_name)

            if storage.exists(thumbnail_name): #checking the path
                print('checking thumbnail name')
                skipped += 1
                continue

            try:
                with storage.open(original_name,"rb") as source:

                    image = Image.open(source)
                    image = ImageOps.exif_transpose(image)

                    # WebP → RGB
                    if image.mode != "RGB":
                        image = image.convert("RGB")

                    
                    # Conversion
                    image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.Resampling.LANCZOS,)

                    # Prepare the image for saving
                    output = BytesIO()
                    
                    # Save the image as WEBP
                    image.save(output, format="WEBP", quality=THUMBNAIL_QUALITY, method=6)
                    

                    # Save the BytesIO object to the ImageField with the new filename
                    thumbnail_data = output.getvalue()

                    

                    self.stdout.write(
                        f"thumbnail_data type = {type(thumbnail_data)}"
                    )

                    self.stdout.write(
                        f"thumbnail_data size = {len(thumbnail_data)}"
)
                    storage.save(thumbnail_name,ContentFile(thumbnail_data),)
                    
                    created += 1

                    self.stdout.write(
                    self.style.SUCCESS(
                        f"CREATED: {thumbnail_name}"
                    )
                )
            
            except (IOError, SyntaxError, Exception) as e:
            
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