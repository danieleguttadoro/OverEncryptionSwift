
#!/bin/bash
echo "-----------------------------------INSTALL ENCSWIFT--------------------------------------------"
sudo rm -rf /opt/stack/swift/swift
sudo cp -r /home/stack/swift  /opt/stack/swift/

sudo rm /etc/swift/proxy-server.conf
sudo stow -t /etc/swift/ -S /home/stack/swift/usr/stow/etc/swift

sudo rm /opt/stack/swift/swift.egg-info/entry_points.txt
sudo stow -t /opt/stack/swift/swift.egg-info/ -S /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/
