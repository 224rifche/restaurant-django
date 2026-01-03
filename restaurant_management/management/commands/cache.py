from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.core.cache import caches
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Gestion avancée du cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Vider tous les caches (Redis, sessions, etc.)'
        )
        parser.add_argument(
            '--sessions',
            action='store_true',
            help='Vider uniquement le cache des sessions'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['all']:
            self.clear_all_caches()
        elif options['sessions']:
            self.clear_sessions()
        else:
            self.clear_default_cache()
        
        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Opération terminée en {elapsed:.2f} secondes')
        )

    def clear_default_cache(self):
        """Vide le cache par défaut"""
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cache par défaut vidé avec succès'))

    def clear_all_caches(self):
        """Vide tous les caches configurés"""
        # Vider le cache par défaut
        cache.clear()
        
        # Vider les caches spécifiques
        for cache_name in settings.CACHES:
            try:
                caches[cache_name].clear()
                self.stdout.write(
                    self.style.SUCCESS(f'Cache "{cache_name}" vidé avec succès')
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f'Erreur lors du vidage du cache {cache_name}: {str(e)}')
                )
        
        # Vider les sessions
        self.clear_sessions()

    def clear_sessions(self):
        """Vide le cache des sessions"""
        from django.contrib.sessions.models import Session
        Session.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Sessions vidées avec succès'))