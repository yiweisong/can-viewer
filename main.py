import argparse
import can
import cantools
import time
import os
from rich.console import Console
from rich.table import Table

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="CAN Message Viewer")
    parser.add_argument("--dbc", required=True, help="Path to the DBC file")
    parser.add_argument("--interface", required=True, help="CAN interface name (e.g., 'can0')")
    parser.add_argument("--channel", required=True, help="CAN channel (e.g., 'vcan0')")
    parser.add_argument("--bitrate", type=int, default=500000, help="CAN bitrate (default: 500000)")
    
    return parser.parse_args()

def load_dbc(dbc_path):
    """加载 DBC 文件"""
    try:
        return cantools.database.load_file(dbc_path)
    except Exception as e:
        print(f"Failed to load DBC file: {e}")
        os._exit(1)

def setup_can_interface(interface, channel, bitrate):
    """设置 CAN 接口"""
    try:
        if interface == 'bmcan':
            return can.interface.Bus(bustype=interface, channel=0, bitrate=bitrate, data_bitrate=2000000, tres=True, is_fd=False)
        elif type == 'pcan':
            return can.interface.Bus(bustype=interface, bitrate=bitrate, data_bitrate=2000000, tres=True, is_fd=False)

        return can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate)
    except Exception as e:
        print(f"Failed to setup CAN interface: {e}")
        os._exit(1)

def parse_can_message(db, message):
    """解析 CAN 消息"""
    try:
        decoded = db.decode_message(message.arbitration_id, message.data)
        return decoded
    except KeyError:
        return None  # 如果消息 ID 不在 DBC 文件中

def main():
    # 解析命令行参数
    args = parse_arguments()

    # 加载 DBC 文件
    db = load_dbc(args.dbc)

    # 设置 CAN 接口
    bus = setup_can_interface(args.interface, args.channel, args.bitrate)

    # 初始化 Rich 控制台
    console = Console()

    # 存储解析后的消息
    parsed_messages = []

    try:
        while True:
            # 读取 CAN 消息
            message = bus.recv(timeout=1)
            if message is None:
                continue

            # 解析 CAN 消息
            decoded_message = parse_can_message(db, message)
            if decoded_message:
                parsed_messages.append({
                    "id": f"0x{message.arbitration_id:X}",
                    "timestamp": f"{message.timestamp:.3f}",
                    "data": decoded_message
                })

            # 显示解析结果
            table = Table(title="CAN Messages")
            table.add_column("ID", justify="right")
            table.add_column("Timestamp", justify="right")
            table.add_column("Data", justify="left")

            for msg in parsed_messages[-10:]:  # 只显示最近 10 条消息
                table.add_row(msg["id"], msg["timestamp"], str(msg["data"]))

            console.clear()
            console.print(table)

            time.sleep(0.1)  # 定期刷新

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()