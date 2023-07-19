sources = [
    {
        'name': 'ThreatCrowd',
        'url': 'https://www.threatcrowd.org/',
        'ioc_selectors': {
            'IP Address': '.result > .ip > a',
            'Domain': '.result > .domain > a',
            'URL': '.result > .url > a',
            'Hash': '.result > .hash > a',
        }
    },
    {
        'name': 'PunkSPIDER',
        'url': 'https://www.punkspider.org/',
        'ioc_selectors': {
            'URL': '.iochash',
        }
    },
    {
        'name': 'ThreatMiner',
        'url': 'https://www.threatminer.org/',
        'ioc_selectors': {
            'Domain': 'tr > td:nth-child(3)',
            'IP Address': 'tr > td:nth-child(4)',
            'Hash': 'tr > td:nth-child(5)',
        }
    },
    # Add more sources as needed
]
