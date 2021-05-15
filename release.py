# -*- coding: utf-8 -*-
import time
import requests
import json
import datetime

#事前に取得したYouTube API key [AIzaSyAITHT-Lt_26UQgJ4PhE5hg6niYrN_Ldbc][AIzaSyCUQKEW69T7oOkNXiKLe29B86HgWsqaRAc]
YT_API_KEY = 'AIzaSyAITHT-Lt_26UQgJ4PhE5hg6niYrN_Ldbc'
starttime = ''
elapsedtime = ''

def get_chat_id(yt_url):
    '''
    https://developers.google.com/youtube/v3/docs/videos/list?hl=ja
    '''
    video_id = yt_url.replace('https://www.youtube.com/watch?v=', '')
    print('video_id : ', video_id)

    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()

    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
        print('get_chat_id done!')
    else:
        chat_id = None
        print('NOT live')

    return chat_id

def get_chat(chat_id, pageToken, log_file,rank,elap):
    '''
    https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
    '''
    url        = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params     = {'key': YT_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails'}
    cnt        = 0
    max_cnt    = 0
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data   = requests.get(url, params=params).json()

    try:
        for item in data['items']:
            channelId = item['snippet']['authorChannelId']
            msg       = item['snippet']['displayMessage']
            usr       = item['authorDetails']['displayName']
            time      = data['items'][0]['snippet']['publishedAt']
            time      = time.translate(str.maketrans({'T':' '}))
            #timeをdate型に変換、小数点が表示されたら上を実行
            try:
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z') 
            except:
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z')                
            #経過時間＝コメントされた時間ー配信開始時間
            elapsedtime = time - starttime 
            #elapsedtimeをstr型に変換、小数点以下をtmp[1]に格納
            tmp = str(elapsedtime).split('.')
            elapsedtime = tmp[0]
            #supChat   = item['snippet']['superChatDetails']
            #supStic   = item['snippet']['superStickerDetails']
            #特定ワードの設定
            try:
                if 'うま' in msg[:]:
                    cnt += 1
                elif 'ウマ' in msg[:]:
                    cnt += 1
                elif '上手' in msg[:]:
                    cnt += 1
                elif 'うめ' in msg[:]:
                    cnt += 1
                elif 'ないす' in msg[:]:
                    cnt += 1
                elif 'ナイス' in msg[:]:
                    cnt += 1
                elif 'Nice' in msg[:]:
                    cnt += 1
                elif 'nice' in msg[:]:
                    cnt += 1
                elif 'つよ' in msg[:]:
                    cnt += 2
                elif 'つっ' in msg[:]:
                    cnt += 2
                elif '強' in msg[:]:
                    cnt += 1
                elif 'やば' in msg[:]:
                    cnt += 2
                elif 'やべ' in msg[:]:
                    cnt += 2
                elif 'ヤバ' in msg[:]:
                    cnt += 2
                elif 'すげ' in msg[:]:
                    cnt += 1
                elif 'スゲ' in msg[:]:
                    cnt += 1
                elif 'すっげ' in msg[:]:
                    cnt += 1
                elif 'えっぐ' in msg[:]:
                    cnt += 2
                elif 'えぐ' in msg[:]:
                    cnt += 2
                elif '3たて' in msg[:]:
                    cnt += 5
                elif '3タテ' in msg[:]:
                    cnt += 5
            except:
                pass
            #最大値が超えたらカウントに代入
            try:
                if max_cnt < cnt:
                    max_cnt = cnt
            except:
                pass
            log_text = elapsedtime, msg, cnt,rank,elap
            #csvファイルとコンソールに出力
            with open(log_file, 'a') as f:
                print(log_text, file=f)
                print(log_text)
        #最大値,時間表示
        for num in range(0,6):
            if max_cnt > rank[num]:
                rank.insert(num,max_cnt)
                elap.insert(num,str(elapsedtime))
                del rank[5]
                del elap[5]
                break
                
    except:
        pass

    return data['nextPageToken']

def getLivedetails(yt_url):
    '''
    GET https://www.googleapis.com/youtube/v3/videos
    '''
    url    = 'https://www.googleapis.com/youtube/v3/videos'
    video_id = yt_url.replace('https://www.youtube.com/watch?v=', '')
    params = {'key': YT_API_KEY, 'part': 'liveStreamingDetails', 'id':video_id }
    global starttime
    
    data   = requests.get(url, params=params).json()   
    starttime = data['items'][0]['liveStreamingDetails']['actualStartTime']     #type(starttime) -> str
    #starttimeのTを空白に置き換え
    starttime = starttime.translate(str.maketrans({'T':' '}))
    try:
        starttime = datetime.datetime.strptime(starttime,"%Y-%m-%d %H:%M:%S%z")
    except:
        starttime = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S.%f%z')

def main(yt_url):
    slp_time        = 15 #sec
    iter_times      = 2880 #回
    take_time       = slp_time / 60 * iter_times
    rank = [0,0,0,0,0]
    elap = [0,0,0,0,0]
    print('{}分後　終了予定'.format(take_time))
    print('work on {}'.format(yt_url))

    log_file = yt_url.replace('https://www.youtube.com/watch?v=', '') + '.csv'
    with open(log_file, 'a') as f:
        print('{} のチャット欄を記録します。'.format(yt_url), file=f)
    chat_id  = get_chat_id(yt_url)
    getLivedetails(yt_url)
    nextPageToken = None
    for ii in range(iter_times):
        try:
            print('------------------API Request Start !------------------')
            print()
            nextPageToken = get_chat(chat_id, nextPageToken, log_file,rank,elap)
            time.sleep(slp_time)
            print('------------------Sleep Time End !------------------\n')
        except:
            break


if __name__ == '__main__':
    yt_url = input('Input YouTube URL > ')
    main(yt_url)