#!/usr/bin/env bash

sudo cp /home/stack/swift/common/middleware/encrypt.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/key_master.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/catalogue.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/crypto_functions.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/connection.py /opt/stack/swift/swift/common/middleware

sudo cp /home/stack/swift/usr/stow/home/vagrant/.vimrc /home/vagrant/

sudo mkdir -m 755 -p /opt/stack/sel-daemon/
#sudo mkdir -m 755 -p /opt/stack/sel-daemon/config
sudo mkdir -m 755 -p /opt/stack/sel-daemon/logs
sudo mkdir -m 755 -p /opt/stack/sel-daemon/keys

sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/catalogue.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/connection.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/create_user.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/simplekeystone.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/pub.key /opt/stack/sel-daemon/keys/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/pvt.key /opt/stack/sel-daemon/keys/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/mk.key /opt/stack/sel-daemon/keys/
#sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/config/daemon.ini /opt/stack/sel-daemon/config/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/logs/event.log /opt/stack/sel-daemon/logs/

sudo chmod +x /opt/stack/sel-daemon/daemon.py

sudo rm -r -fd /usr/local/lib/python2.7/dist-packages/Crypto/

#cat /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/entry_points.txt | sudo tee /opt/stack/swift/swift.egg-info/entry_points.txt
#cat /home/stack/swift/usr/stow/etc/swift/proxy-server.conf | sudo tee /etc/swift/proxy-server.conf
