# PuppetOverencryptionSwift.git
# copy in 'devstack-vagrant/puppet/modules/devstack/templates/local.erb' after <% if defined?(@manager_extra_services) %>

# substitute folder 'swift' with 'OverEncryptionSwift'
sudo rm -rf /opt/stack/swift/swift
sudo cp -r /home/stack/swift  /opt/stack/swift/

# copy in 'devstack-vagrant/puppet/modules/swift/manifests/init.pp
sudo chmod +x /opt/stack/swift/swift/usr/command-git.sh
