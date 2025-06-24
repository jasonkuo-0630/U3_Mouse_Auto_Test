import asyncio
from robot_ws_client import RobotWebSocketClient

class NonBlockingRobotClient:
    def __init__(self):
        self.client = RobotWebSocketClient()
        self.message_queue = asyncio.Queue()
        self.running = False
        
    async def handle_route_event(self, data):
        """將消息放入隊列，不阻塞"""
        await self.message_queue.put(data)
        
    async def message_processor(self):
        """後台處理消息的任務"""
        while self.running:
            try:
                # 等待消息，但設置超時避免永久阻塞
                data = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # 處理消息
                print("📥 Received /route_ctrl_event:")
                print("→ 狀態：", data.get("status", "-"))
                print("→ 目標：", data.get("target", "-"))
                
                # 標記任務完成
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                # 超時是正常的，繼續循環
                continue
            except Exception as e:
                print(f"❌ 處理消息時發生錯誤: {e}")
                
    async def connect(self, host):
        self.client.set_message_handler(self.handle_route_event)
        await self.client.connect(host)
        self.running = True
        
        # 啟動後台消息處理任務
        self.processor_task = asyncio.create_task(self.message_processor())
        
    async def disconnect(self):
        self.running = False
        if hasattr(self, 'processor_task'):
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        await self.client.disconnect()
        
    # 代理方法
    async def send_delivery_command(self, tables):
        return await self.client.send_delivery_command(tables)
        
    async def send_continue(self):
        return await self.client.send_continue()
        
    async def send_return(self):
        return await self.client.send_return()
        
    async def send_stop(self):
        return await self.client.send_stop()

async def get_user_input(prompt):
    """異步獲取用戶輸入"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

async def main():
    client = NonBlockingRobotClient()
    await client.connect("localhost")  # 修改為實際IP
    
    try:
        while True:
            print("\n--- 操作選單 ---")
            print("1. 送餐（send_delivery_command）")
            print("2. Continue")
            print("3. Return")
            print("4. Stop")
            print("q. 離開")
            
            choice = await get_user_input("選擇操作 (1/2/3/4/q): ")
            choice = choice.strip()
            
            if choice == "1":
                tables = await get_user_input("請輸入桌號（如 A01,A02）: ")
                await client.send_delivery_command(tables)
            elif choice == "2":
                await client.send_continue()
            elif choice == "3":
                await client.send_return()
            elif choice == "4":
                await client.send_stop()
            elif choice.lower() == "q":
                break
            else:
                print("❓ 無效的選項")
                
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
