from django.core.management.base import BaseCommand
from PIL import Image
from core.models import ActivityImage

class Command(BaseCommand):
    help = "Find empty/broken activity images. Add --delete to remove the broken ones."
    def add_arguments(self, parser): parser.add_argument("--delete", action="store_true")
    def handle(self, *args, **opts):
        bad = 0
        for i in ActivityImage.objects.select_related("activity"):
            try:
                with Image.open(i.image.path) as im: im.load()
            except Exception:
                bad += 1; self.stdout.write(f"BROKEN: #{i.pk}  {i.image.name}  ({i.activity})")
                if opts["delete"]: i.image.delete(save=False); i.delete()
        self.stdout.write(f"{bad} broken image(s)." + (" Deleted - upload them again in the admin." if opts["delete"] and bad else ""))