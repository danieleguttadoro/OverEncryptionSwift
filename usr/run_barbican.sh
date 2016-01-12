sudo apt-get update
sudo apt-get install libffi-dev libssl-dev git -y
mv barbican/contrib/devstack/lib/barbican devstack/lib/

mv barbican/contrib/devstack/local.conf devstack/

mv barbican/contrib/devstack/extras.d/70-barbican.sh devstack/extras.d/
sudo ./devstack/tools/create-stack-user.sh
sudo mv devstack/ /opt/stack/
rm -rf barbican/
chown -R stack:stack /opt/stack/devstack/
su - stack
cd /opt/stack/devstack/
