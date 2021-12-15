from setuptools import setup, find_namespace_packages

setup(name='personal_assistant',
      version='1',
      description='Maintaining a personal address book.',
      url='https://github.com/korshunov-olexiy/personal_assistant',
      author='Александр Бернатович, Angelika Kuzmina, Olexii Korshunov',
      author_email='leaderr99@gmail.com, angelikak199712@gmail.com, korshunov.olexiy@gmail.com',
      license='MIT',
      #packages=['personal_assistant'],
      install_requires=['pick==1.2.0'],
      packages=find_namespace_packages()
    #   entry_points={
    #       'console_scripts':
    #       ['clean-folder=personal_assistant.clean:sort_dir']
    #   }
      )
