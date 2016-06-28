#!/bin/bash
cd /home/stack/swift/

echo "Insert branch to commit: master"

read branch
sudo git checkout $branch

cat /opt/stack/swift/swift/common/middleware/key_master.py | sudo tee /home/stack/swift/common/middleware/key_master.py
cat /opt/stack/swift/swift/common/middleware/encrypt.py | sudo tee /home/stack/swift/common/middleware/encrypt.py
cat /opt/stack/swift/swift/common/middleware/catalog_manager.py | sudo tee /home/stack/swift/common/middleware/catalog_manager.py
cat /opt/stack/swift/swift/common/middleware/key_manager.py | sudo tee /home/stack/swift/common/middleware/key_manager.py
cat /opt/stack/swift/swift/common/middleware/connection.py | sudo tee /home/stack/swift/common/middleware/connection.py

#cat /etc/swift/proxy-server.conf  | sudo tee /home/stack/swift/usr/stow/etc/swift/proxy-server.conf

cat /opt/stack/sel-daemon/catalog_manager.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/catalog_manager.py
cat /opt/stack/sel-daemon/create_user.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/create_user.py
cat /opt/stack/sel-daemon/simplekeystone.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/simplekeystone.py
cat /opt/stack/sel-daemon/keys/pub.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/pub.key
cat /opt/stack/sel-daemon/keys/pvt.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/pvt.key
cat /opt/stack/sel-daemon/keys/mk.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/keys/mk.key
cat /opt/stack/sel-daemon/daemon.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py
cat /opt/stack/sel-daemon/init.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/init.py
cat /opt/stack/sel-daemon/__init__.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/__init__.py
cat /opt/stack/sel-daemon/logs/log | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/logs/log
cat /opt/stack/sel-daemon/myLogger.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/myLogger.py
cat /opt/stack/sel-daemon/middleware/__init__.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/middleware/__init__.py
cat /opt/stack/sel-daemon/middleware/connection.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/middleware/connection.py
cat /opt/stack/sel-daemon/middleware/headers.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/middleware/headers.py

sudo git add *

echo "Insert message for commit (space with _):"
read -e msg

sudo git commit -m $msg
sudo git push origin $branch
