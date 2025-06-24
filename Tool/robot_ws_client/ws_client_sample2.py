import asyncio
from robot_ws_client import RobotWebSocketClient

class AutoDeliveryRobot:
    def __init__(self):
        self.client = RobotWebSocketClient()
        self.arrival_event = asyncio.Event()
        self.current_target = None
        
    async def handle_route_event(self, data):
        """處理路由事件"""
        status = data.get("status")
        target = data.get("target")
        
        print(f"📥 收到事件 - 狀態: {status}, 目標: {target}")
        
        # 檢查是否到達目標位置
        if status == "arrived" and target == self.current_target:
            print(f"✅ 已到達 {target}")
            self.arrival_event.set()
            
    async def wait_for_arrival(self, target):
        """等待到達指定目標"""
        self.current_target = target
        self.arrival_event.clear()
        await self.arrival_event.wait()
        
    async def connect(self, host):
        """連接到機器人"""
        self.client.set_message_handler(self.handle_route_event)
        await self.client.connect(host)
        
    async def disconnect(self):
        """斷開連接"""
        await self.client.disconnect()
        
    async def run_delivery_cycle(self, cycles=20):
        """執行送餐循環"""
        for i in range(cycles):
            print(f"\n🔄 第 {i+1} 次循環 (共 {cycles} 次)")
            
            for n in range(9):  # 0~8
                table = f"{n}M"
                print(f"🚀 前往 {table}...")
                await self.client.send_delivery_command(table)
                await self.wait_for_arrival(table)
                print("⏰ 等待 3 秒...")
                await asyncio.sleep(3)

            # 8~0（不重複8M，因為上面剛去過8M）
            for n in range(7, -1, -1):
                table = f"{n}M"
                print(f"🚀 前往 {table}...")
                await self.client.send_delivery_command(table)
                await self.wait_for_arrival(table)
                print("⏰ 等待 3 秒...")
                await asyncio.sleep(3)    

        print("🎉 完成所有循環！")
        # 呼叫 return 指令
        print("🏠 執行返回指令...")
        await self.client.send_return()        

async def main():
    robot = AutoDeliveryRobot()
    
    try:
        # 連接到機器人
        await robot.connect("192.168.1.193")  # 修改為實際IP
        print("🔗 已連接到機器人")
        
        # 執行 20 次循環
        await robot.run_delivery_cycle(5)
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        await robot.disconnect()
        print("👋 已斷開連接")

if __name__ == "__main__":
    asyncio.run(main())
