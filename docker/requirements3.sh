 sudo -H cat requirements.txt | grep -v '#' | xargs -n 1 sudo -H pip3 install --upgrade
