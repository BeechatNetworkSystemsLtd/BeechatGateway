import miniupnpc
import random
import itertools
import ipaddress


class port_manager():
    def __init__(self):
        ''' initialize a uPnP '''        
        try:
            self.upnp = miniupnpc.UPnP()
            self.discover()
        except Exception as err:
            print(err)
            raise ValueError("uPnP is not running or not properly responding ")
        self.available_ports = [int(i) for i in range(1024, 65536, 1)]
    
    
    def port_ban(self, port):
        ''' remove port from available list '''
        if port in self.available_ports:
            self.available_ports.pop(self.available_ports.index(port))
    
        
    def discover(self) -> Exception:
        ''' checking uPnP workness '''
        devices = self.upnp.discover()
        self.upnp.selectigd()
        ipaddress.ip_address(self.upnp.lanaddr)
        ext_ip = self.upnp.externalipaddress()
        return ((devices, ext_ip))
        
        
    def used_ports(self) -> None:
        ''' uPnP used ports '''
        for i in itertools.count(start=0):
            result = self.upnp.getgenericportmapping(i)            
            if result == None:
                break  
            print(f"Used port: {result}")
            (port, proto, (internal_host, internal_port), desc, c, d, timelife) = result
            if port in self.available_ports:
                self.available_ports.pop(self.available_ports.index(port))


    def unmap_ports(self) -> None:
        while True:
            result = self.upnp.getgenericportmapping(0)
            if result == None:
                break
            print(f"Close the: {result}")
            (port, proto, (internal_host, internal_port), desc, c, d, timelife) = result
            self.unmapport(port=port, proto=proto)
            if int(port) not in self.available_ports:
                self.available_ports.append(int(port))
    
    
    def mapport(self, port=None, proto="TCP", tries=20) -> tuple((bool, str)):
        ''' mapping port is argument or random choice from the self.available_ports '''
        self.used_ports()
        for i in range(tries):
            if port:
                _port = port
            else:
                _port = random.choice(self.available_ports)
            try:
                result = self.upnp.addportmapping(int(_port), proto, self.upnp.lanaddr, int(_port), str(_port), '')
                break
            except Exception as err:
                self.port_ban(_port)
                result = False                
                print(f"Mapping is unsuccessful. Tried port: {_port}")     
                _port = "-1"      
                if port:                                       
                    break
            finally:
                self.port_ban(_port)
        return ((result, str(_port)))
        
        
    def unmapport(self, port: int, proto="TCP") -> bool:
        ''' unmapping port '''
        try:
            result = self.upnp.deleteportmapping(int(port), proto)
        except Exception as err:
            result = False
        finally:
            if int(port) not in self.available_ports:
                self.available_ports.append(int(port))
        return ((result))

if __name__ == "__main__":
    pm = port_manager()
    print(pm.discover())
    (result, port) = pm.mapport()
    print(result, port)
    print(pm.used_ports())
    print(pm.unmapport(int(port)))
    print(pm.used_ports())
    print(pm.unmap_ports(closeall=True))
