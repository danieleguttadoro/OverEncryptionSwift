#!/bin/bash
cd /home/stack/swift/
echo "Insert branch to commit: master, devAle ,devDan"
read branch
sudo git checkout $branch
cat /opt/stack/swift/swift/common/middleware/overencrypt.py | sudo tee /home/stack/swift/common/middleware/overencrypt.py
cat /opt/stack/swift/swift.egg-info/entry_points.txt | sudo tee  /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/entry_points.txt
cat /etc/swift/proxy-server.conf  | sudo tee /home/stack/swift/usr/stow/etc/swift/proxy-server.conf
sudo git add *
echo "Insert message for commit:"
read msg
sudo git commit -m $msg
sudo git push origin $branch
