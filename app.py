import datetime
import os
import sys
import traceback
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import configparser
from linebot.models import (TextSendMessage, QuickReply, QuickReplyButton,MessageEvent, TextMessage, TextSendMessage,PostbackEvent,MessageAction,
                            PostbackTemplateAction,ButtonsTemplate,TemplateSendMessage,StickerSendMessage,URIAction,PostbackAction,ImageCarouselTemplate,ImageCarouselColumn  )

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
##handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
#line_bot_api.push_message(config.get('line-bot', 'channel_id'), TextSendMessage(text='倉庫已連線'))
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
print(channel_access_token,channel_secret)
if channel_secret is None or channel_access_token is None:
    load_dotenv("D:\linebot\para.env")
    channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
    channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
    print('1',channel_access_token,channel_secret)
    if channel_secret is None or channel_access_token is None:
        sys.exit(1)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
#line_bot_api.push_message(os.getenv('LINE_CHANNEL_ID', None), TextSendMessage(text='倉庫已連線'))
worksheet=pysheet_use.login_sheet()
sheet_titles=pysheet_use.check_column_title(worksheet)


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
    if '叫' in user_message:
        line_bot_api.reply_message(event.reply_token, quick_buttom_format('init'))
    elif '買' in user_message:
        split_message=user_message.split(' ')
        today = datetime.date.today()
        food_action, food_name, food_count, food_unit=split_message
        print(sheet_titles)
        pysheet_use.update_all_name_and_count_and_unit(worksheet,sheet_titles,(str(today),food_name, float(food_count), food_unit))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='添加完畢'))
    elif '吃' in user_message:
        split_message=user_message.split(' ')
        today = datetime.date.today()
        food_action, food_name, food_count, food_unit=split_message
        pysheet_use.update_all_name_and_count_and_unit(worksheet,sheet_titles,(str(today),food_name, -1*float(food_count), food_unit))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='更新完畢'))
    elif "換" in user_message:
        buttons_template = ButtonsTemplate(
            title='Hello~我是冰箱精靈',
            text='需要什麼協助',
            actions=[
                PostbackAction(label='購入格式',data='store'),
                PostbackAction(label='吃掉格式',data='eat'),
                PostbackAction(label='清查庫存',data='stock-taking'),
                PostbackAction(label='提醒',data='stock-remind'),
            ]
        )
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text='按鈕樣板', template=buttons_template))
    elif '測試功能' in user_message:
        message=TextSendMessage(
            text='測試',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                            action=MessageAction(label="message", text="one message")
                        ),
                    QuickReplyButton(
                            action=URIAction(label='開啟GOOGLE SHEET',uri='https://docs.google.com/spreadsheets/d/1f3bU44K7SQCFSV6TX48V4dNqQiyWIQA7-kWsIy9xmc0/edit#gid=0')
                        ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif '召喚' in user_message:
        message=TemplateSendMessage(
        alt_text='ImageCarousel template',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url=f'https://th.bing.com/th/id/R.4a39f2d1cd011f477e0263ddefed837c?rik=y95E%2bFc66R6QIA&riu=http%3a%2f%2fi2.kknews.cc%2fBKgSs7BH20OvV5xo8pjREF0zUJOcOVKW5sdTYio%2f0.jpg&ehk=HVi8eG7gBJZGgz3MYbGxUB2UMnnE9ESOJ3t0Sqgiibw%3d&risl=&pid=ImgRaw&r=0',
                    action=PostbackAction(
                            label='卡比卡比',
                            data='dog2'
                        )
                ),
                ImageCarouselColumn(
                    image_url='https://upload.wikimedia.org/wikipedia/en/5/59/Pok%C3%A9mon_Squirtle_art.png',
                    action=PostbackAction(
                            label='傑尼傑尼',
                            data='dog1'
                        )
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
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
    elif postback=='stock-remind':
        sendBack_stock_remind(event)
    elif postback in ['dog1','dog2']:
        sendBack_dog(event,postback)


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
                                label='檢視庫存',
                                data='stock-taking')
                    ),
                    QuickReplyButton(
                        action=PostbackTemplateAction(
                                label='清空庫存',
                                data='stock-clearing')
                    ),
                    QuickReplyButton(
                            action=PostbackAction(label='提醒',data='stock-remind')
                        ),
                ]
            )
        )
    return message

def sendBack_store(event):
    try:
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
        _,names,storages,units=pysheet_use.get_names_and_units(worksheet,sheet_titles)
        item=''
        for x,y in enumerate(names):
            item=item+f'{y} {storages[x]} {units[x]}'+'\n'
        
        message_A = []
        message_A.append(TextSendMessage(text="目前倉庫還有"))
        if item!='':
            message_A.append(TextSendMessage(text=item))
        else:
            message_A.append(StickerSendMessage(package_id = '8525',sticker_id = '16581311'))
            message_A.append(TextSendMessage(text="空氣"))
        line_bot_api.reply_message(event.reply_token,message_A) 
    except Exception as e:
        print('error',traceback.format_exc())
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))
def sendBack_stock_clear(event):
    try:
        worksheet.clear()
        message_A = []
        message_A.append(TextSendMessage(text="全部清掉啦"))
        pysheet_use.check_column_title(worksheet)
        line_bot_api.reply_message(event.reply_token,message_A) 
    except Exception as e:
        print('error',traceback.format_exc())
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))

def sendBack_stock_remind(event):
    try:
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
                line_bot_api.reply_message(event.reply_token,[StickerSendMessage(package_id = '6325',sticker_id = '10979922'),TextSendMessage(text=remind_text)])
    except Exception as e:
        print('error',traceback.format_exc())
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))

def sendBack_dog(event,postback):
    if postback=='dog1':
        try:
            worksheet.clear()
            message_A = []
            message_A.append(TextSendMessage(text="撲通"))
            message_A.append(TextSendMessage(text="全部被捲進水溝啦"))
            pysheet_use.check_column_title(worksheet)
            line_bot_api.reply_message(event.reply_token,message_A) 
        except Exception as e:
            print('error',traceback.format_exc())
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))
    elif postback=='dog2':
        try:
            worksheet.clear()
            message_A = []
            message_A.append(TextSendMessage(text="全部被卡比獸吃掉啦"))
            pysheet_use.check_column_title(worksheet)
            line_bot_api.reply_message(event.reply_token,message_A) 
        except Exception as e:
            print('error',traceback.format_exc())
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='失敗'))  
if __name__ == "__main__":
    app.run()