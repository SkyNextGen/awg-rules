"""Offline regression checks for explicitly requested service coverage."""
from pathlib import Path
import sys
import unittest
import json

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from build import ROOT, domain, lines, prune


class ServiceCoverage(unittest.TestCase):
    def test_required_categories_enabled_once(self):
        categories = lines((ROOT / 'config/v2fly-categories.txt').read_text())
        for category in (
            'nexusmods', 'facebook', 'instagram', 'meta', 'threads',
            'google', 'google-play', 'googlefcm', 'youtube', 'microsoft',
            'netflix', 'nvidia', 'openai', 'category-ai-cn',
            'category-ai-!cn', 'category-ai-chat-!cn', 'category-ai-ru',
            'tiktok', 'spotify', 'soundcloud', 'playstation', 'patreon',
        ):
            self.assertEqual(categories.count(category), 1, category)

    def test_messaging_services_are_separate_refreshable_sources(self):
        cfg = json.loads((ROOT / 'config/sources.json').read_text())
        sources = cfg['service_sources']
        self.assertEqual(set(sources), {'discord', 'telegram', 'whatsapp'})
        for service, entries in sources.items():
            with self.subTest(service=service):
                self.assertTrue(entries)
                self.assertTrue(all(entry.get('kind') in {'v2fly', 'domains'} for entry in entries))
        self.assertTrue(any(entry.get('category') == 'discord' for entry in sources['discord']))
        self.assertTrue(any(entry.get('url', '').endswith('/Services/discord.lst') for entry in sources['discord']))
        self.assertTrue(any(entry.get('category') == 'telegram' for entry in sources['telegram']))
        self.assertTrue(any(entry.get('url', '').endswith('/Services/telegram.lst') for entry in sources['telegram']))
        self.assertTrue(any(entry.get('category') == 'whatsapp' for entry in sources['whatsapp']))
        self.assertFalse(any('Subnets/' in entry.get('url', '') for entries in sources.values() for entry in entries))

    def test_pinned_suffixes_cover_downloads_and_media(self):
        suffixes = prune(domain(value) for value in lines(
            (ROOT / 'config/service-domains.txt').read_text()))
        hosts = (
            'discord.com', 'gateway.discord.gg', 'cdn.discordapp.com',
            'media.discordapp.net', 'images-ext-1.discordapp.net',
            'images-ext-2.discordapp.net', 'voice-region.discord.media',
            'nexusmods.com', 'api.nexusmods.com', 'users.nexusmods.com',
            'staticdelivery.nexusmods.com', 'files.nexus-cdn.com',
            'supporter-files.nexus-cdn.com', 'premium-files.nexus-cdn.com',
        )
        for host in hosts:
            with self.subTest(host=host):
                self.assertTrue(any(host == suffix or host.endswith('.' + suffix)
                                    for suffix in suffixes))
        for shared in ('cloudflare.com', 'googleapis.com', 'amazonaws.com'):
            self.assertNotIn(shared, suffixes)
