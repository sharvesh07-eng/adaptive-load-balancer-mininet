#!/usr/bin/env python3

from mininet.topo import Topo


class AdaptiveLoadBalancerTopo(Topo):

    def build(self):

        # Create four hosts
        client = self.addHost(
            'h1',
            ip='10.0.0.1/24'
        )

        load_balancer = self.addHost(
            'h2',
            ip='10.0.0.2/24'
        )

        backend1 = self.addHost(
            'h3',
            ip='10.0.0.3/24'
        )

        backend2 = self.addHost(
            'h4',
            ip='10.0.0.4/24'
        )

        # Create one Open vSwitch
        switch = self.addSwitch('s1')

        # Connect all hosts to the switch
        self.addLink(client, switch)
        self.addLink(load_balancer, switch)
        self.addLink(backend1, switch)
        self.addLink(backend2, switch)


topos = {
    'adaptive': lambda: AdaptiveLoadBalancerTopo()
}
