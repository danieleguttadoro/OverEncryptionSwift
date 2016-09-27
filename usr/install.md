# Setup Puppet
https://github.com/AlessandroSaullo/devstack-vagrant-enc.git

This is a modified version of puppet. 

  * Introduced module 'swift':
  
  'puppet/swift/manifests/init.pp' to perfom two actions, clone encswift_server (https://github.com/danieleguttadoro/encswift_server.git) into '/home/stack/swift' and make executable 'command-git.sh'  
  * Change file 'devstack/templates/local.erb':
 
  enable_plugin barbican https://git.openstack.org/openstack/barbican stable/mitaka

  ```ruby
  <% if defined?(@manager_extra_services) %>
  
  #execute install.sh
  bash -c "chmod +x /home/stack/swift/usr/install.sh"
  bash -c "/home/stack/swift/usr/install.sh"
  
  #enable extra services
  enable_service <%= @manager_extra_services %>
  
  <% end %>
  ```
  
  to make executable and execute 'install.sh', that substitutes the swift folder into '/opt/stack/swift/' and links 'proxy-server.conf' with the respective version on '/etc/swift/'
