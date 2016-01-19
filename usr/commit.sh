#!/bin/bash
cd /home/stack/swift/
echo "Insert branch to commit: master, devAle ,devDan"
read branch
sudo git checkout $branch
cat /opt/stack/swift/swift/common/middleware/key_master.py | sudo tee /home/stack/swift/common/middleware/key_master.py
cat /opt/stack/swift/swift/common/middleware/encrypt.py | sudo tee /home/stack/swift/common/middleware/encrypt.py
cat /opt/stack/swift/swift/common/middleware/decrypt.py | sudo tee /home/stack/swift/common/middleware/decrypt.py
cat /opt/stack/swift/swift/common/middleware/catalog_functions.py | sudo tee /home/stack/swift/common/middleware/catalog_functions.py
cat /etc/swift/proxy-server.conf  | sudo tee /home/stack/swift/usr/stow/etc/swift/proxy-server.conf
sudo git add *
echo "Insert message for commit:"
read -e msg
sudo git commit -m $msg
sudo git push origin $branch
