import json
import telnetlib

import requests
import paramiko
import time
def load_config():
    data={}
    with open('config_auto.json', 'r') as f:
        data = json.loads(f.read())
    return data


def read_sid_from_igp(host,port,username,password,config):
    def get_end_sid(hostname):
        tn.write(bytes("show isis database verbose internal {} | include End\n".format(hostname),"utf-8"))
        result = tn.read_until(b"RP/0/RP0/CPU0")
        print(result)
        output = str(result).split("\\r\\n")
        for i in range(0,len(output)):
            if "END SID" in output[i]:
                end_sid=output[i].split()[2]
                return end_sid
        return None

    tn = telnetlib.Telnet(host,port)
    tn.write(b"\r\n")
    tn.read_until(b"Username")
    tn.write(bytes("{}\n".format(username),"utf-8"))
    tn.read_until(b"Password")
    tn.write(bytes("{}\n".format(password),"utf-8"))
    tn.read_until(b"RP/0/RP0/CPU0")
    tn.write(b"term len 0\n")
    tn.read_until(b"RP/0/RP0/CPU0")
    # tn.write(b"show isis neighbors\n")
    # result = tn.read_until(b"RP/0/RP0/CPU0")
    # output = str(result).split("\\r\\n")
    # isis_neighbour=""
    # for i in range(0,len(output)):
    #     if "System Id" in output[i]:
    #         isis_neighbour=output[i+1].split()[0]
    #         break
    # print(isis_neighbour)
    # print(result)
    for node,router in config["node_hostname"].items():
        sid=get_end_sid(router)
        config["node_sid"][node]=sid
    tn.write(b"exit\n")



class PathFinder(object):
    def __init__(self,ip,username,password,node_table):
        self.ip=ip
        self.username=username
        self.password=password
        self.node_table=node_table
        self.ip_table=dict(zip(self.node_table.values(),self.node_table.keys()))

        pass

    def _build_url(self):
        return "http://{}:8080/lsp/compute/simple".format(self.ip)

    def compute(self,source,dest,method):
        def build_payload():
            params= {
                "type":"sr",
                "source":self.node_table[source],
                "destination":self.node_table[dest],
                "protected":1
            }
            assert method in ['igp','te','latency']
            params['metric-{}'.format(method)]=1
            return params
        response = requests.get(self._build_url(),params=build_payload(),auth=(self.username, self.password))
        if response.status_code!=200:
            response.raise_for_status()
        return self._calculate_path(response.json())

    def _calculate_path(self,json):
        jumps=[]
        for data in json["data_gpbkv"][0]["fields"]:
            jumps.append(self.ip_table[data['fields'][2]["string_value"]])
        return jumps

class Translator(object):
    def __init__(self,node_sid):
        self.node_sid=node_sid
    def translate(self,node):
        return self.node_sid[node]



class VPPController_CLI(object):
    """
    Multiple ways to configure the VPP controller.
    This is the implimentation of the CLI APP by VPP.
    """
    def __init__(self,ip,username,password):
        """
        Use SSH to connect to vpp instance and configure
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=ip, port=22, username=username, password=password)

        pass

    def show_policy(self):
        stdin, stdout, stderr = self.client.exec_command("vppctl show sr policies")

        for line in stdout.readlines():
            print(line)

        # print(stdout.read())

        # output=subprocess.check_output(["vppctl","show","sr","policies"])
        # for line in output.splitlines():
        #     print(line)


    def add_policy(self,bsid,sids):
        assert type(bsid)==str
        assert type(sids)==list and len(sids)!=0
        sid_param=""
        for sid in sids:
            sid_param=sid_param+"next {} ".format(sid)
        cmd="vppctl sr policy add bsid {} {} encap".format(bsid,sid_param)
        print("EXEC： "+cmd)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        for line in stdout.readlines():
            if "already a FIB entry for the BindingSID address" in line:
                print("ERROR : SID Already exist")
                return False
            else:
                print(line)

        pass

    def update_steering(self,ip_prefix,bsid):
        cmd="vppctl sr steer l3 {} via bsid {}".format(ip_prefix,bsid)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        for line in stdout.readlines():
            print(line)


    def del_policy(self,bsid):
        cmd="vppctl sr policy del bsid {}".format(bsid)
        stdin, stdout, stderr =self.client.exec_command(cmd)
        print(stdout)
        pass



if __name__ == '__main__':
    config = load_config()

    print("VPP Demo Controller")
    config=load_config()
    # If you don't have End SID already set, you need this for reading the END SID.
    read_sid_from_igp(config["xtc_node"]["ip"],config["xtc_node"]["port"],config["xtc_node"]["username"],config["xtc_node"]["password"],config)
    # If you don't have End SID already set, you need this for reading the END SID.
    xtc=config["xtc_node"]
    pf=PathFinder(xtc["ip"],xtc["username"],xtc["password"],config["node_table"])

    # print(pf.compute("node1","node3","latency"))
    # print(pf.compute("node1","node2","latency"))
    # print(pf.compute("node2","node1","latency"))
    # print(pf.compute("node3","node1","latency"))
    vpp=config["vpp_node"]
    vpp=VPPController_CLI(vpp["ip"],vpp["username"],vpp["password"])
    # vpp.show_policy()
    # vpp.add_policy("fc00:1::999:10",["fc00:1::a","fc00:2::a"])
    # # vpp.show_policy()
    # # vpp.add_policy("fc00:1::999:10",["fc00:1::a","fc00:2::a"])
    #
    # vpp.del_policy("fc00:1::999:10")
    # vpp.update_steering("10.0.1.0/24",)
    # vpp.show_policy()
    trans=Translator(config["node_sid"])
    route1=[]
    route2=[]
    while True:
        result1=pf.compute("node1", "node2", "latency")
        result2=pf.compute("node1", "node3", "latency")
        changed=False
        if result1!=route1:
            print("Node1 to Node2 Route updating : {}".format(result1))
            sid_list=[trans.translate(i) for i in result1]
            sid_list.append(config["node_dx4_sid"][0])
            vpp.del_policy("fc00:1::999:12")
            vpp.add_policy("fc00:1::999:12",sid_list)
            vpp.update_steering(config["node_prefix"][0],"fc00:1::999:12")
            route1=result1
            changed=True
        if result2!=route2:
            print("Node1 to Node3 Route updating : {}".format(result2))
            sid_list=[trans.translate(i) for i in result2]
            sid_list.append(config["node_dx4_sid"][1])
            vpp.del_policy("fc00:1::999:13")
            vpp.add_policy("fc00:1::999:13",sid_list)
            vpp.update_steering(config["node_prefix"][1],"fc00:1::999:13")
            route2=result2
            changed=True
        if changed:
            print("SRv6 Policy Updated:")
            vpp.show_policy()
        time.sleep(5)