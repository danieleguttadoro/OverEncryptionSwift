#!/usr/bin/env bash
sudo cp /home/stack/swift/common/middleware/encrypt.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/key_master.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/catalogue.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/usr/stow/home/vagrant/.vimrc /home/vagrant/
sudo cp /home/stack/swift/common/middleware/crypto_functions.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/connection.py /opt/stack/swift/swift/common/middleware
sudo mkdir -m 755 -p /opt/stack/sel-daemon/
#sudo mkdir -m 755 -p /opt/stack/sel-daemon/config
#sudo mkdir -m 755 -p /opt/stack/sel-daemon/log
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/rabbit_connection.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/receive_message.py /opt/stack/sel-daemon/
#sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/config/daemon.ini /opt/stack/sel-daemon/config/
#sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/log/daemon.log /opt/stack/sel-daemon/log/
sudo chmod +x /opt/stack/sel-daemon/daemon.py
sudo pip install --upgrade pip
sudo pip install pika
#cat /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/entry_points.txt | sudo tee /opt/stack/swift/swift.egg-info/entry_points.txt
#cat /home/stack/swift/usr/stow/etc/swift/proxy-server.conf | sudo tee /etc/swift/proxy-server.conf
