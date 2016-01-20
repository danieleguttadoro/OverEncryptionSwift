#!/usr/bin/env bash
sudo cp /home/stack/swift/common/middleware/encrypt.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/decrypt.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/common/middleware/key_master.py /opt/stack/swift/swift/common/middleware
sudo cp /home/stack/swift/usr/stow/home/vagrant/.vimrc /home/vagrant/
sudo mkdir -m 755 -p /opt/stack/sel-daemon/
sudo mkdir -m 755 -p /opt/stack/sel-daemon/config
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py /opt/stack/sel-daemon/
sudo cp /home/stack/swift/usr/stow/home/stack/sel-daemon/config/daemon.ini /opt/stack/sel-daemon/config/
#cat /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/entry_points.txt | sudo tee /opt/stack/swift/swift.egg-info/entry_points.txt
#cat /home/stack/swift/usr/stow/etc/swift/proxy-server.conf | sudo tee /etc/swift/proxy-server.conf
