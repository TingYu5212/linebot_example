import datetime
import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import configparser
from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton,MessageEvent, TextMessage, TextSendMessage,PostbackEvent,
    MessageAction,PostbackTemplateAction,ButtonsTemplate,TemplateSendMessage) 
#from linebot.v3.messaging import MessagingApi
import pysheet_use

app = Flask(__name__)

def update_date(config_source):
    config_source['line-bot']['today']=str(datetime.date.today())
    print(datetime.date.today())
    with open('config.ini', 'w') as configfile:
        config_source.write(configfile)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
worksheet=pysheet_use.login_sheet()
sheet_titles=pysheet_use.check_column_title(worksheet)

remind_text='倉庫有點臭臭的，注意'+'\n'
need_remind=False
if str(datetime.date.today())!=config.get('line-bot', 'today'):
    update_date(config)
    init_dates,init_names,init_storages,init_units=pysheet_use.get_names_and_units(worksheet,sheet_titles)
    for i ,date in enumerate(init_dates):
        date_split=date.split('-')
        some_days=abs(datetime.date.today()-datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))).days
        if some_days>=3:
            need_remind=True
            remind_text=remind_text+f'{init_dates[i]} {init_names[i]} {init_storages[i]}{init_units[i]}'+'\n'
    if need_remind:
        line_bot_api.push_message(config.get('line-bot', 'channel_id'), TextSendMessage(text=remind_text))

#https://ithelp.ithome.com.tw/articles/10217767
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    #reply_text = "您說了：" + user_message
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    if '叫' in user_message:
        line_bot_api.reply_message(
            event.reply_token, quick_buttom_format('init')
            )
    elif '買' in user_message:
        split_message=user_message.split(' ')
        today = datetime.date.today()
        food_action, food_name, food_count, food_unit=split_message
        #worksheet=pysheet_use.login_sheet()
        #sheet_titles=pysheet_use.check_column_title(worksheet)
        print(sheet_titles)
        pysheet_use.update_all_name_and_count_and_unit(worksheet,sheet_titles,(str(today),food_name, float(food_count), food_unit))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='添加完畢'))
    elif '吃' in user_message:
        split_message=user_message.split(' ')
        today = datetime.date.today()
        food_action, food_name, food_count, food_unit=split_message
        #worksheet=pysheet_use.login_sheet()
        #sheet_titles=pysheet_use.check_column_title(worksheet)
        pysheet_use.update_all_name_and_count_and_unit(worksheet,sheet_titles,(str(today),food_name, -1*float(food_count), food_unit))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='更新完畢'))
    elif "換" in user_message:
        buttons_template = ButtonsTemplate(
            title='Hello~我是冰箱精靈',
            text='需要什麼協助',
            actions=[
                PostbackTemplateAction(label='購入格式',data='store'),
                PostbackTemplateAction(label='吃掉格式',data='eat'),
                PostbackTemplateAction(label='清查庫存',data='stock-taking'),
                PostbackTemplateAction(label='清空庫存',data='stock-clearing')
            ]
        )
        line_bot_api.reply_message(
            event.reply_token, TemplateSendMessage(alt_text='按鈕樣板', template=buttons_template))
    return
    
@handler.add(PostbackEvent)
def handle_postback(event):
    postback=event.postback.data
    print('postback',postback)
    if postback=='store':
        sendBack_store(event)
    elif postback=='eat':
        sendBack_eat(event)
    elif postback=='stock-taking':
        sendBack_stock(event)
    elif postback=='stock-clearing':
        sendBack_stock_clear(event)
    #line_bot_api.reply_message(
    #        event.reply_token, quick_buttom_format('othoer'))

def quick_buttom_format(input):
    if input=='init':
        output_text='Hello~我是倉庫精靈'
    else:
        output_text='還需要什麼幫忙嗎'
    message=TextSendMessage(
            text=output_text,
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=PostbackTemplateAction(
                                label='購入格式',
                                data='store')
                    ),
                    QuickReplyButton(
                        action=PostbackTemplateAction(
                                label='吃掉格式',
                                data='eat')
                    ),
                    QuickReplyButton(
                        action=PostbackTemplateAction(
                                label='清查庫存',
                                data='stock-taking')
                    ),
                    QuickReplyButton(
                        action=PostbackTemplateAction(
                                label='清空庫存',
                                data='stock-clearing')
                    ),
                    #QuickReplyButton(
                    #        action=MessageAction(label="message", text="one message")
                    #    ),
                ]
            )
        )

    return message

def sendBack_store(event):
    try:
        #worksheet=pysheet_use.login_sheet()
        #sheet_titles=pysheet_use.check_column_title(worksheet)
        _,names,_,units=pysheet_use.get_names_and_units(worksheet,sheet_titles)
        item=''
        for x,y in zip(names,units):
            item=item+f'{x} {y}'+'\n'
        #print('item',item)
        message_A = []
        message_A.append(TextSendMessage(text="填寫格式::買 金針菇 11 包"))
        message_A.append(TextSendMessage(text=item))
        line_bot_api.reply_message(event.reply_token,message_A) 
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))
def sendBack_eat(event):
    try:
        #worksheet=pysheet_use.login_sheet()
        #sheet_titles=pysheet_use.check_column_title(worksheet)
        _,names,_,units=pysheet_use.get_names_and_units(worksheet,sheet_titles)
        item=''
        for x,y in zip(names,units):
            item=item+f'{x} {y}'+'\n'
        message_A = []
        message_A.append(TextSendMessage(text="填寫格式::吃 金針菇 13 包"))
        message_A.append(TextSendMessage(text=item))
        line_bot_api.reply_message(event.reply_token,message_A) 
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))
def sendBack_stock(event):
    try:
        #worksheet=pysheet_use.login_sheet()
        #sheet_titles=pysheet_use.check_column_title(worksheet)
        _,names,storages,units=pysheet_use.get_names_and_units(worksheet,sheet_titles)
        item=''
        for x,y in enumerate(names):
            item=item+f'{y} {storages[x]} {units[x]}'+'\n'
        message_A = []
        message_A.append(TextSendMessage(text="目前倉庫還有"))
        message_A.append(TextSendMessage(text=item))
        line_bot_api.reply_message(event.reply_token,message_A) 
    except Exception as e:
        print('error',traceback.format_exc())
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))
def sendBack_stock_clear(event):
    try:
        worksheet.clear()
        message_A = []
        message_A.append(TextSendMessage(text="全部清掉啦"))
        line_bot_api.reply_message(event.reply_token,message_A) 
    except Exception as e:
        print('error',traceback.format_exc())
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))


if __name__ == "__main__":
    app.run()