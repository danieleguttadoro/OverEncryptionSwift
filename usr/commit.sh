#!/bin/bash
cd /home/stack/swift/
echo "Insert branch to commit: master"
read branch
sudo git checkout $branch
cat /opt/stack/swift/swift/common/middleware/key_master.py | sudo tee /home/stack/swift/common/middleware/key_master.py
cat /opt/stack/swift/swift/common/middleware/encrypt.py | sudo tee /home/stack/swift/common/middleware/encrypt.py
cat /opt/stack/swift/swift/common/middleware/config.py | sudo tee /home/stack/swift/common/middleware/config.py
cat /opt/stack/swift/swift/common/middleware/catalogue.py | sudo tee /home/stack/swift/common/middleware/catalogue.py
cat /opt/stack/swift/swift/common/middleware/crypto_functions.py | sudo tee /home/stack/swift/common/middleware/crypto_functions.py
cat /opt/stack/swift/swift/common/middleware/connection.py | sudo tee /home/stack/swift/common/middleware/connection.py
cat /opt/stack/sel-daemon/receive_message.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/receive_message.py
cat /opt/stack/sel-daemon/rabbit_connection.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/rabbit_connection.py
#cat /etc/swift/proxy-server.conf  | sudo tee /home/stack/swift/usr/stow/etc/swift/proxy-server.conf
cat /opt/stack/sel-daemon/daemon.py | sudo tee /home/stack/swift/usr/stow/home/stack/sel-daemon/daemon.py
sudo git add *
echo "Insert message for commit:"
read -e msg
sudo git commit -m $msg
sudo git push origin $branch
