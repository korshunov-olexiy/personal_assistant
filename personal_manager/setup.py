from setuptools import setup, find_namespace_packages

setup(name='personal_manager',
      version='0.7',
      description='Maintaining a personal address book.',
      url='https://github.com/korshunov-olexiy/personal_assistant',
      author='Александр Бернатович, Angelika Kuzmina, Olexii Korshunov',
      author_email='leaderr99@gmail.com, angelikak199712@gmail.com, korshunov.olexiy@gmail.com',
      license='MIT',
      install_requires=['pick==1.2.0', 'wheel'],
      packages=find_namespace_packages(),
      entry_points={'console_scripts': ['personal-manager=personal_manager.personal_manager:main']}
      )
