# 運行以下程式需安裝模組: line-bot-sdk, flask, pyquery
# 安裝方式，輸入指令:
# pip install line-bot-sdk flask pyquery

#本地端測試 
# 1、ngrok有開啟 ./ngrok http 準備要啟動的port號碼 免費版每次都不一樣 已讀=line的伺服器有收到訊息不代表通道有打開 每次都要啟動一次 網址會不一樣 要重新貼到linebot 後台Webhook URL
# 2、啟動應用程式 python app.py 

# ctrl c 可以把應用程式關閉
# 用line測試
#若有學過git指令 不要使用現在代碼做紀錄現在程式碼的狀態 金鑰會外露
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    StickerMessage,
    LocationMessage,
)

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    StickerMessageContent,
    LocationMessageContent,
)

import os
# 如何把另個檔案的變數(模組)  引用到另一個.py檔案
# 盡量放在最上方
#-----------------------------------------------方案練習
from modules.reply import faq,menu #modules資料夾
from modules.currency import get_exchange_table
table = get_exchange_table()
# print(table)

app = Flask(__name__)

#隱蔽金鑰
#在應用程式啟動之前
#很重要的資料取名要全大寫
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN) #將此替換成你的_CHANNEL_ACCESS_TOKEN
handler = WebhookHandler(CHANNEL_SECRET)#將此替換成你的_CHANNEL_SECRET #密碼錯誤會收不到使用者訊息

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature'] #line用來驗證我們帳密有沒有寫對 
    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.") #如果寫錯就會顯示
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event): 
    with ApiClient(configuration) as api_client:
        # 當使用者傳入文字訊息時
        line_bot_api = MessagingApi(api_client)
        # 在此的 evnet.message.text 即是 Line Server 取得的使用者文字訊息
        user_msg = event.message.text #使用者傳來的訊息
        print("event",event) #自己打的!! 
        print("-" * 30)
        print("使用者傳入的文字訊息是:", user_msg)
        print("-" * 30)
        bot_msg = menu #<--  #TextMessage(text=f"What you said is: {user_msg}") #可以改傳給使用者看的文字訊息 #機器人回傳的訊息
        # if user_msg 存在於 faq 字典內，就覆蓋掉之前在user_msg訂的回覆
        if user_msg in faq:
            bot_msg = faq[user_msg]
        
        elif user_msg in table:
            buy = table[user_msg]["buy"]
            sell = table[user_msg]["sell"]
            bot_msg = TextMessage(text=f"{user_msg} 買價:{buy} 賣價:{sell}資料取自於台灣銀行公告牌價" )
        
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                # 放置於 ReplyMessageRequest 的 messages 裡的物件即是要回傳給使用者的訊息
                # 必須注意由於 Line 有其使用的內部格式
                # 因此要回覆的訊息務必使用 Line 官方提供的類別來產生回應物件
                messages=[
                    bot_msg,
                    TextMessage(text="HELLOW WORLD") #自己打的~ #想要傳HELLOW WORLD給使用者看 #物件無法顯示PYTHON型別 所以在LINE上看到的文字不是字串 而是一個文字類別物件
                ]
            )
        )

@handler.add(MessageEvent, message=StickerMessageContent) #python 沒有貼圖資料型別 是line工程師設計出來類別
def handle_sticker_message(event):
    with ApiClient(configuration) as api_client:
        # 當使用者傳入貼圖時
        print("機器人收到貼圖囉") #自己改的
        line_bot_api = MessagingApi(api_client)
        sticker_id = event.message.sticker_id
        package_id = event.message.package_id
        keywords_msg = "這張貼圖背後沒有關鍵字"
        if len(event.message.keywords) > 0:
            keywords_msg = "這張貼圖的關鍵字有:"
            keywords_msg += ", ".join(event.message.keywords)
        # 可以使用的貼圖清單
        # https://developers.line.biz/en/docs/messaging-api/sticker-list/
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    StickerMessage(package_id="6325", sticker_id="10979904"),  #傳貼圖的反例 要要提供StickrtID 跟 pakageID
                    TextMessage(text=f"你剛才傳入了一張貼圖，以下是這張貼圖的資訊:"),
                    TextMessage(text=f"貼圖包ID為 {package_id} ，貼圖ID為 {sticker_id} 。"),
                    TextMessage(text=keywords_msg),
                ]
            )
        )

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    with ApiClient(configuration) as api_client:
        # 當使用者傳入地理位置時
        line_bot_api = MessagingApi(api_client)
        latitude = event.message.latitude
        longitude = event.message.longitude
        address = event.message.address
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=f"You just sent a location message."),
                    TextMessage(text=f"The latitude is {latitude}."),
                    TextMessage(text=f"The longitude is {longitude}."),
                    TextMessage(text=f"The address is {address}."),
                    LocationMessage(title="Here is the location you sent.", address=address, latitude=latitude, longitude=longitude)
                ]
            )
        )

# 如果應用程式被執行執行
if __name__ == "__main__":
    print("[伺服器應用程式開始運行]")
    # 取得遠端環境使用的連接端口，若是在本機端測試則預設開啟於port=5001
    port = int(os.environ.get('PORT', 5001))
    print(f"[Flask即將運行於連接端口:{port}]")
    print(f"若在本地測試請輸入指令開啟測試通道: ./ngrok http {port} ")
    # 啟動應用程式
    # 本機測試使用127.0.0.1, debug=True
    # Heroku部署使用 0.0.0.0
    app.run(host="0.0.0.0", port=port, debug=True)
