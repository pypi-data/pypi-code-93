import os

import lxcb.info


def bootstrap():
    # set up the default container config
    config = os.path.join(lxcb.info.home, '.config/lxc')
    if not os.path.isdir(config):
        os.makedirs(config)

    with open(os.path.join(config, 'default.conf'), 'w') as f:
        f.write('''
lxc.net.0.type = veth
lxc.net.0.link = lxcbr0
lxc.net.0.flags = up

# allows mapping folders between host and container
lxc.idmap = u 0 100000 1000
lxc.idmap = u 1000 1000 1
lxc.idmap = u 1001 101000 64536

lxc.idmap = g 0 100000 1000
lxc.idmap = g 1000 1000 1
lxc.idmap = g 1001 101000 64536
''')

    print('please run the following commands:')
    print('''
# creates network bridge
sudo tee /etc/default/lxc-net <<EOF
USE_LXC_BRIDGE="true"
EOF

# allow user to access network bridge
sudo tee /etc/lxc/lxc-usernet <<EOF
$USER veth lxcbr0 10
EOF

sudo systemctl restart lxc-net

# allow unprivileged container namespaces
sudo tee /etc/sysctl.d/lxc-unprivileged.conf <<EOF
kernel.unprivileged_userns_clone=1
EOF

sudo sysctl --system
''')
