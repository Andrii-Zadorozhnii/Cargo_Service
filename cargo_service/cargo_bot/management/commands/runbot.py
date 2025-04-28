from django.core.management.base import BaseCommand
from cargo_bot.bot import main
import asyncio

class Command(BaseCommand):
    help = 'Запуск телеграм-бота'

    def handle(self, *args, **options):
        asyncio.run(main())