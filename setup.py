from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='exploface',
      version='0.1',
      description='',
      long_description=readme(),
      # classifiers=[
      #   'Development Status :: under developement',
      #   'License :: nothing yet',
      #   'Programming Language :: Python :: 2.7',
      #   'Topic :: astronomical :: calculations :: minerals',
      # ],
      keywords='',
      #url='https://github.com/bldevries/opacity_calculator',
      author='B.L. de Vries',
      author_email='',
      license='',
      packages=['exploface'],
      # package_data={
      #     'write_elan_eaf_files': ['main.py'],
      # },
      # install_requires=[
      #     'markdown',
      # ],
      # test_suite='nose.collector',
      # tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['funniest-joke=funniest.command_line:main'],
      # },
      #include_package_data=True,
      zip_safe=True)