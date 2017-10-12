 sudo -H cat requirements.txt | grep -v '#' | xargs -n 1 sudo pip3 install --upgrade
