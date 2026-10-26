FROM gitpod/workspace-python
USER gitpod
RUN pyenv install -s 3.12.16 && pyenv global 3.12.16
