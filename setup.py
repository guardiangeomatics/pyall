from setuptools import setup

if __name__ == '__main__':
    # Run setup script
    setup(name='pyall',
          version='1.50',
          description='python module to read an Kongsberg .ALL file',
          author='pktrigg',
          author_email='p.kennedy@fugro.com',
          url='https://github.com/pktrigg/pyall',
          license='Apache License 2.0',
          setup_requires=[],
          packages=['pyall'],
          use_2to3=False,
          classifiers=[
              'License :: OSI Approved :: Apache Software License',
              'Intended Audience :: Developers',
              'Intended Audience :: Other Audience',
              'Intended Audience :: Science/Research',
              'Natural Language :: English',
              'Topic :: Scientific/Engineering',
              'Programming Language:: Python:: 3:: Only'
          ])
