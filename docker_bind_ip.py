#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
__author__ = 'zihepeng'
__date__ = '2016-01-06'
'''
import docker,os,time

try:
	connect = docker.Client(base_url='unix:///var/run/docker.sock',version='1.6.2',timeout=120)
#	print connect.version()
except:
	exit()


def Instance(id,br,addr,gw):
	try:
		container_info = connect.inspect_container(resource_id=id)
		pid = str(container_info['State']['Pid'])
	except:
		pid = 0
	
	if int(pid) != 0:
		if not os.path.exists('/var/run/netns'):
			os.makedirs('/var/run/netns')
		source_namespace = '/proc/'+pid+'/ns/net'
		destination_namespace = '/var/run/netns/'+pid+''
		if not os.path.exists(destination_namespace):
			link = 'ln -s %s %s' %(source_namespace,destination_namespace)
			bridge_veth = 'veth'+pid
			container_net = 'container'+pid
			error_log = '/var/log/docker_bind_ip.log'
			os.system(link)
			os.system('ip link add %s type veth peer name %s 2>> %s' % (bridge_veth,container_net,error_log))
			os.system('brctl addif %s %s 2>> %s' %(br,bridge_veth,error_log))
			os.system('ip link set %s up 2>> %s' %(bridge_veth,error_log))
			os.system('ip link set %s netns %s 2>> %s' %(container_net,pid,error_log))
			os.system('ip netns exec %s ip link set dev %s name eth0 2>> %s' %(pid,container_net,error_log))
			os.system('ip netns exec %s ip link set eth0 up 2>> %s' %(pid,error_log))
			os.system('ip netns exec %s ip addr add %s dev eth0 2>> %s' %(pid,addr,error_log))
			os.system('ip netns exec %s ip route add default via %s 2>> %s' %(pid,gw,error_log))

syspid = os.fork()

if syspid == 0:
	while True:
		file = open('./containers.cfg')
		if file:
			for line in file:
				line = line.strip('\n')
				args = line.split()
				Instance(*args)
		file.close()
		time.sleep(10)
else:
	exit()
	
