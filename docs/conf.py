import sys
sys.path.insert(0, '../')

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
source_suffix = '.rst'
master_doc = 'index'
project = u'chaino'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = "0.1.0"
# The full version, including alpha/beta/rc tags.
release = "0.1.0"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'chaino-librarydoc'
