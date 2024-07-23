pip uninstall cjudge --break-system-packages
python3 -m build
pip install dist/cjudge-0.0.1.tar.gz --break-system-packages