# Setup Puppet
https://github.com/danieleguttadoro/PuppetEncryptionSwift.git

This is a modified version of puppet. 

  * Introduced module 'swift':
    puppet/swift/manifests/init.pp 
  to perfom two actions, clone OverEncryptionSwift into '/home/stack/swift' and make executable 'command-git.sh'  
  * Change file 'devstack/templates/local.erb':
    <% if defined?(@manager_extra_services) %>

    # execute install.sh
    bash -c "chmod +x /home/stack/swift/usr/install.sh"
    bash -c "/home/stack/swift/usr/install.sh"
  
    #enable extra services
    enable_service <%= @manager_extra_services %>
    <% end %>
  to make executable and execute 'install.sh', that substitutes the swift folder into '/opt/stack/swift/' and links 'proxy-server.conf' and 'entry_points.txt' with the respective version on '/etc/swift/' and   '/opt/stack/swift/swift.egg-info/'
