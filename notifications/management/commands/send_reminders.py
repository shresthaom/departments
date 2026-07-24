from django.core.management.base import BaseCommand

from notifications.reminders import send_reminders


class Command(BaseCommand):

    help = "Send appointment reminders."

    def handle(self, *args, **kwargs):

        send_reminders()

        self.stdout.write(

            self.style.SUCCESS(

                "Reminder check completed."

            )

        )