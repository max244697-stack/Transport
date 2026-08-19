import os

# Import production settings by default
if os.environ.get('DEBUG') == 'True':
    from .dev import *
else:
    from .prod import *