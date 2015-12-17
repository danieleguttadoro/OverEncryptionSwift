sudo cp /home/stack/swift/common/middleware/overencrypt.py /opt/stack/swift/swift/common/middleware
cat /home/stack/swift/usr/stow/opt/stack/swift/swift.egg-info/entry_points.txt | sudo tee /opt/stack/swift/swift.egg-info/entry_points.txt
cat /home/stack/swift/usr/stow/etc/swift/proxy-server.conf | sudo tee /etc/swift/proxy-server.conf
