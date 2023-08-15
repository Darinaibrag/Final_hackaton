from django.core.management.base import BaseCommand
from post.telegram_bot import main

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting the Telegram bot...'))
        main()
