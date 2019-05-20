# SRv6 VPP & XTC 功能演示用控制器

本代码为配合SRv6实战（第三篇）中使用控制器算路实时下发策略进行验证的简易控制器。

https://www.sdnlab.com/23218.html

其中main.py为文中使用的控制器代码

main_auto_fetchSID_version.py为改进版，使用IGP来获取NCS5500路由器上End对应的SID

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