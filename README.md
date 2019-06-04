# SRv6 VPP & XTC 功能演示用控制器

本代码为配合SRv6实战（第三篇）中使用控制器算路实时下发策略进行验证的简易控制器。

https://www.sdnlab.com/23218.html

其中main.py为文中使用的控制器代码

main_auto_fetchSID_version.py为改进版，使用IGP来获取NCS5500路由器上End对应的SID

main_auto_etcd.py为最新版，该版本无需XTC控制器，将网络中一台NCS5500或者XR设备作为控制器算路即可。

每台NCS5500通过docker的辅助模块，从gRPC获取自己的SID信息，并同步到etcd，该脚本通过etcd取到SID信息，在进行算路。




原版配置文件如下：（config.json）
```json
{
  "xtc_node":{
    "ip":"10.xx.xx.xx",
    "username":"cisco",
    "password":"cisco"
  },
  "vpp_node":{
    "ip":"10.xx.xx.xx",
    "username":"root",
    "password":"cisco"
  },
  "node_list":["node1","node2","node3"],
  "node_table":{
      "node1":"192.168.0.1",
      "node2":"192.168.0.2",
      "node3":"192.168.0.3"
  },
  "node_sid":{
      "node1": "fc00:a:1:0:1::",
      "node2": "fc00:b:1:0:1::",
      "node3": "fc00:c:1:0:1::"
  },
  "node_prefix":["10.0.1.0/24","10.0.2.0/24"],
  "node_dx4_sid":["fc00:2::a","fc00:3::a"]
}

```

新版配置文件如下：（config_auto.json）
```json
{
  "xtc_node":{
    "ip":"10.xx.xx.xx",
    "port":"23", //Telnet port
    "username":"cisco",
    "password":"cisco123"
  },
  "vpp_node":{
    "ip":"10.75.58.120",
    "username":"root",
    "password":"cisco123"
  },
  "node_list":["node1","node2","node3"],
  "node_table":{
      "node1":"192.168.0.1",
      "node2":"192.168.0.2",
      "node3":"192.168.0.3"
  },
  "node_hostname":{ //路由器的hostname配置
      "node1": "RouterA",
      "node2": "RouterB",
      "node3": "RouterC"
  },
  "node_sid":{
  },
  "node_prefix":["10.0.1.0/24","10.0.2.0/24"],
  "node_dx4_sid":["fc00:2::a","fc00:3::a"]
}
```

etcd版本配置文件如下：（config_etcd.json）
```json
{
  "xtc_node":{
    "ip":"10.xx.xx.xx",
    "username":"cisco",
    "password":"cisco123"
  },
  "vpp_node":{
    "ip":"10.75.58.120",
    "username":"root",
    "password":"cisco123"
  },
  "node_list":["node1","node2","node3"],
  "node_table":{
      "node1":"2.2.2.2",
      "node2":"3.3.3.3",
      "node3":"1.1.1.1"
  },
  "etcd_node":{    //运行etcd的ncs55/linux 信息
      "ip":"10.xx.xx.xx",
      "port":"2379"
  },
  "node_hostname":{
      "node1": "RouterA",
      "node2": "RouterB",
      "node3": "SR-PCE"
  },
  "node_sid":{
  },
  "node_prefix":["10.0.1.0/24","10.0.2.0/24"],
  "node_dx4_sid":["fc00:2::a","fc00:3::a"]
}
```


使用新版的自动获取SID的版本，需要XTC与网络中的一台NCS5500建立ISIS，并在NCS5500上配置
```
router isis 1
 address-family ipv6 unicast
  metric-style wide
  segment-routing srv6
   locator 你在NCS55上定义的locator名称
   !
```
之后按教程配置好node_hostname 即可


使用etcd版本，需要在设备上开启gRPC
```
grpc
 port 57777
 no-tls
 address-family ipv4
!
```
并参考教程

在IOS XR上运行ETCD

https://github.com/ljm625/ios-xr-etcd

在IOS XR上运行SID采集器，并同步到ETCD中

https://github.com/ljm625/xr-srv6-etcd

需要注意的是，全网内每台配置了SRv6 SID的IOS XR设备均需要运行第二个容器（SID采集器）来获取到他的SID信息。
