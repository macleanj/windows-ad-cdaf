Vagrant.configure("2") do |config|
  config.vm.box = "cdaf/WindowsServerDC"
  config.vm.box_version = "2020.05.14"
  config.vm.network "forwarded_port", guest: 53, host: 1053, protocol: 'tcp'
  config.vm.network "forwarded_port", guest: 53, host: 1053, protocol: 'udp'
  config.vm.network "forwarded_port", guest: 88, host: 1088, protocol: 'tcp'
  config.vm.network "forwarded_port", guest: 88, host: 1088, protocol: 'udp'
  config.vm.network "forwarded_port", guest: 389, host: 1389, protocol: 'tcp'
  config.vm.network "forwarded_port", guest: 389, host: 1389, protocol: 'udp'
  # config.vm.network "forwarded_port", guest: 22, host: 2222
  
  # default: 389 (guest) => 389 (host) (adapter 1)
  # default: 5985 (guest) => 55985 (host) (adapter 1)
  # default: 5986 (guest) => 55986 (host) (adapter 1)
  # default: 22 (guest) => 2222 (host) (adapter 1)

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
    vb.cpus = 2
    vb.name = "ActiveDirectory"
  end

end
