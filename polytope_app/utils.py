from prompt_toolkit.styles import Style

__all__ = ['custom_style', 'git_custom_style']

custom_style = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:cyan bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:cyan'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#a3a3a3 italic'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


git_custom_style = Style([
    ('qmark', 'fg:magenta bold'),
    ('question', 'bold fg:magenta'),
    ('answer', 'fg:magenta bold'),
    ('pointer', 'fg:magenta bold'),
    ('highlighted', 'fg:magenta bold'),
    ('selected', 'fg:magenta'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#a3a3a3 italic'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])
