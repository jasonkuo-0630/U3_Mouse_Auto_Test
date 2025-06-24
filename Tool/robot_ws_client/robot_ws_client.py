import asyncio
import json
import websockets

class RobotWebSocketClient:
    def __init__(self,log_func=print):
        # 將print輸出字串 能夠以CMD呈現 並存至LOG檔內
        self.log = log_func
        # 儲存 websocket 連線物件
        self.websocket = None
        # 接收訊息的回呼函式（由使用者外部自訂）
        self.receive_callback = None
        # 監聽 WebSocket 訊息的 asyncio 背景任務
        self.listen_task = None

    async def connect(self, ip="localhost", port=8000):
        """
        建立 WebSocket 連線並啟動監聽任務
        預設連線到本機 localhost:8000
        """
        uri = f"ws://{ip}:{port}/ws"    
        self.websocket = await websockets.connect(uri)
        # 啟動背景任務來持續接收訊息
        self.listen_task = asyncio.create_task(self._listen())
        self.log(f"✅ Connected to WebSocket at {uri}")

    async def disconnect(self):
        """
        中斷 WebSocket 連線並結束監聽任務
        """
        if self.websocket:
            await self.websocket.close()
            self.log("🛑 Disconnected from WebSocket")

    async def send_delivery_command(self, table_name):
        """
        發送前往指定桌號的送餐指令
        範例: "A01" 或 "A01,A02"
        """
        await self._send("/route_ctrl_event", {"deliver_to_tables": table_name})

    async def send_continue(self):
        """
        當抵達其中一桌時，發送此指令讓機器人繼續前往下一桌
        """
        await self._send("/route_ctrl_event", {"event": "continue"})

    async def send_return(self):
        """
        要求機器人返回出餐點（初始位置）
        """
        await self._send("/route_ctrl_event", {"event": "return"})

    async def send_stop(self):
        """
        要求機器人緊急停止（類似 UI 上的停止按鈕）
        """
        await self._send("/ui_event", {"event": "stop_hardware"})

    def set_message_handler(self, callback):
        """
        設定接收到狀態訊息時要呼叫的處理函式
        回呼函式參數將是一個 dict（status / target）
        """
        self.receive_callback = callback

    async def _send(self, topic, data):
        """
        實際執行送出資料到 WebSocket 的方法
        會組合成 dict 格式再轉為 JSON 字串
        """
        if self.websocket:
            msg = {"topic": topic, "data": data}
            await self.websocket.send(json.dumps(msg))

    async def _listen(self):
        """
        背景監聽 WebSocket 訊息
        一收到 "/route_ctrl_event" 的主題就會解析並交由 callback 處理
        """
        try:
            async for message in self.websocket:
                try:
                    msg_obj = json.loads(message)  # 將 JSON 字串轉為物件
                    if msg_obj.get("topic") == "/route_ctrl_event":
                        data = msg_obj.get("data")
                        # 有些資料本身還是 JSON 字串，要再解一次
                        parsed = json.loads(data) if isinstance(data, str) else data
                        if self.receive_callback:
                            await self.receive_callback(parsed)
                except Exception as e:
                    print("Error parsing message:", e)
        except Exception as e:
            print("Connection closed or error occurred:", e)
