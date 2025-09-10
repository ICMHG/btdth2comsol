"""
ThermalNetList模型类
对应C++的ThermalNetList类，管理热网络列表
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class NetlistNode:
    """网络节点类，对应C++的NetlistNode"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化NetlistNode
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.node_type: str = ""
        self.temperature: float = 0.0
        self.power: float = 0.0
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name
    
    def get_node_type(self) -> str:
        """获取节点类型"""
        return self.node_type
    
    def get_temperature(self) -> float:
        """获取温度"""
        return self.temperature
    
    def get_power(self) -> float:
        """获取功率"""
        return self.power
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.node_type = json_data.get("nodeType", "")
            self.temperature = json_data.get("temperature", 0.0)
            self.power = json_data.get("power", 0.0)
            
            logger.debug(f"Loaded NetlistNode: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load NetlistNode from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "nodeType": self.node_type,
                "temperature": self.temperature,
                "power": self.power
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert NetlistNode to JSON: {e}")
            raise


class NetlistConnection:
    """网络连接类，对应C++的NetlistConnection"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化NetlistConnection
        
        Args:
            json_data: JSON数据字典
        """
        self.from_node: str = ""
        self.to_node: str = ""
        self.thermal_resistance: float = 0.0
        self.connection_type: str = ""
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_from_node(self) -> str:
        """获取起始节点"""
        return self.from_node
    
    def get_to_node(self) -> str:
        """获取目标节点"""
        return self.to_node
    
    def get_thermal_resistance(self) -> float:
        """获取热阻"""
        return self.thermal_resistance
    
    def get_connection_type(self) -> str:
        """获取连接类型"""
        return self.connection_type
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.from_node = json_data.get("fromNode", "")
            self.to_node = json_data.get("toNode", "")
            self.thermal_resistance = json_data.get("thermalResistance", 0.0)
            self.connection_type = json_data.get("connectionType", "")
            
            logger.debug(f"Loaded NetlistConnection: {self.from_node} -> {self.to_node}")
            
        except Exception as e:
            logger.error(f"Failed to load NetlistConnection from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "fromNode": self.from_node,
                "toNode": self.to_node,
                "thermalResistance": self.thermal_resistance,
                "connectionType": self.connection_type
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert NetlistConnection to JSON: {e}")
            raise


class ThermalNetList:
    """热网络列表类，对应C++的ThermalNetList"""
    
    def __init__(self):
        """初始化ThermalNetList"""
        self.nodes: List[NetlistNode] = []
        self.connections: List[NetlistConnection] = []
        self.netlist_name: str = ""
    
    def add_node(self, node: NetlistNode) -> None:
        """添加节点"""
        self.nodes.append(node)
        logger.debug(f"Added netlist node: {node.get_name()}")
    
    def add_connection(self, connection: NetlistConnection) -> None:
        """添加连接"""
        self.connections.append(connection)
        logger.debug(f"Added netlist connection: {connection.get_from_node()} -> {connection.get_to_node()}")
    
    def get_nodes(self) -> List[NetlistNode]:
        """获取所有节点"""
        return self.nodes
    
    def get_connections(self) -> List[NetlistConnection]:
        """获取所有连接"""
        return self.connections
    
    def get_node_by_name(self, name: str) -> Optional[NetlistNode]:
        """根据名称获取节点"""
        for node in self.nodes:
            if node.get_name() == name:
                return node
        return None
    
    def get_netlist_name(self) -> str:
        """获取网络列表名称"""
        return self.netlist_name
    
    def set_netlist_name(self, name: str) -> None:
        """设置网络列表名称"""
        self.netlist_name = name
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.netlist_name = json_data.get("netlistName", "")
            
            # 加载节点
            if "nodes" in json_data:
                nodes_data = json_data["nodes"]
                for node_data in nodes_data:
                    node = NetlistNode(node_data)
                    self.add_node(node)
            
            # 加载连接
            if "connections" in json_data:
                connections_data = json_data["connections"]
                for connection_data in connections_data:
                    connection = NetlistConnection(connection_data)
                    self.add_connection(connection)
            
            logger.debug(f"Loaded ThermalNetList: {self.netlist_name} with {len(self.nodes)} nodes and {len(self.connections)} connections")
            
        except Exception as e:
            logger.error(f"Failed to load ThermalNetList from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "netlistName": self.netlist_name,
                "nodes": [node.to_json() for node in self.nodes],
                "connections": [connection.to_json() for connection in self.connections]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert ThermalNetList to JSON: {e}")
            raise
