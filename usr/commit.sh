#!/bin/bash
cd /home/stack/swift/

echo "Insert branch to commit: master"

read branch
sudo git checkout $branch

cat /opt/stack/swift/swift/common/middleware/key_master.py | sudo tee /home/stack/swift/common/middleware/key_master.py
cat /opt/stack/swift/swift/common/middleware/encrypt.py | sudo tee /home/stack/swift/common/middleware/encrypt.py
cat /opt/stack/swift/swift/common/middleware/catalogue.py | sudo tee /home/stack/swift/common/middleware/catalogue.py
cat /opt/stack/swift/swift/common/middleware/crypto_functions.py | sudo tee /home/stack/swift/common/middleware/crypto_functions.py
cat /opt/stack/swift/swift/common/middleware/connection.py | sudo tee /home/stack/swift/common/middleware/connection.py

#cat /etc/swift/proxy-server.conf  | sudo tee /home/stack/swift/usr/stow/etc/swift/proxy-server.conf

cat /opt/stack/sel-daemon/connection.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/connection.py
cat /opt/stack/sel-daemon/catalogue.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/catalogue.py
cat /opt/stack/sel-daemon/create_user.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/create_user.py
cat /opt/stack/sel-daemon/simplekeystone.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/simplekeystone.py
cat /opt/stack/sel-daemon/pub.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/pub.key
cat /opt/stack/sel-daemon/pvt.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/pvt.key
cat /opt/stack/sel-daemon/mk.key | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/mk.key
cat /opt/stack/sel-daemon/daemon.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py
cat /opt/stack/sel-daemon/logs/event.log | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/logs/event.log

sudo git add *

echo "Insert message for commit (space with _):"
read -e msg

sudo git commit -m $msg
sudo git push origin $branch
