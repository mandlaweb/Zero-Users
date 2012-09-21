from setuptools import find_packages, setup


setup(
    # Basic package information:
    name = 'zero-users',
    version = '0.1.5',
    packages = ['users'],
    
    # Packaging options:
    zip_safe = False,
    include_package_data = True,
    
    # Package dependencies:
    install_requires = ['zero-common>=0.1.2', 'Django>=1.3.1', 'South>=0.7.3'],
    
    # Metadata for PyPI:
    author = 'Jose Maria Zambrana Arze',
    author_email = 'contact@josezambrana.com',
    license = 'apache license v2.0',
    url = 'http://github.com/mandlaweb/Zero-Users',
    keywords = 'zero users app',
    description = 'Simple app with views and models to manage users and profiles',
    long_description = "Another simple app to manage profiles in django."
)

