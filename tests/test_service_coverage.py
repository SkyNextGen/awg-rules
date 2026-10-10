"""Offline regression checks for explicitly requested service coverage."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from build import ROOT, domain, lines, prune


class ServiceCoverage(unittest.TestCase):
    def test_required_categories_enabled_once(self):
        categories = lines((ROOT / 'config/v2fly-categories.txt').read_text())
        for category in ('discord', 'nexusmods'):
            self.assertEqual(categories.count(category), 1, category)

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
