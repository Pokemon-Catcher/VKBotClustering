# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload

import random
import argparse
import traceback
import config as cfg
from threading import Thread
import time

from skimage import io
from collections import deque

import subprocess

   
def parse_args():
    parser = argparse.ArgumentParser()  # Для параметров
    parser.add_argument('--vk_token', type=str, default=cfg.VK_TOKEN)
    parser.add_argument('--vk_group_id', type=int, default=cfg.GROUP_ID)
    return parser.parse_args()

answers=deque()

params = parse_args()

vk_session = vk_api.VkApi(token=params.vk_token)
uploader = VkUpload(vk_session)  # Понадобится для загрузки своих изображений в вк
long_poll = VkBotLongPoll(vk_session, params.vk_group_id)


def start_clustering(n_clusters, image, answer): #PROGRESS HANDLER RUNS CLUSTERING SUBPROCESS
    print(n_clusters, image, answer)
    timer=time.time()
    process = subprocess.Popen(['python', '-u', 'clusterizer.py', '--n_clusters', str(n_clusters), '--image', image, '--name', str(answer['peer_id'])], stdout=subprocess.PIPE, bufsize=1)
    value=0
    while True:
        if time.time() != timer:
            timer=time.time()
            if process.poll() is not None:
                print('finished')
                try:
                    uploaded_photos = uploader.photo_messages("../{}.png".format(answer['peer_id']))
                    # Можно загрузить несколько изображений сразу.
                    # Выглядит так же как и attachment которые мы получаем в сообщении
                    uploaded_photo = uploaded_photos[0]
                    # Но сейчас у нас только одно.
                    
                    photo_attachment = f'photo{uploaded_photo["owner_id"]}_{uploaded_photo["id"]}'
                    answer.update({'attachment' : photo_attachment, 'random_id': random.randint(0, 100000)})
                except FileNotFoundError as err:
                    full_stack_trace = traceback.format_exc()
                    print("BLIN {}".format(full_stack_trace))
                    answer.update({'message' : 'There is not so many colors at the image. Try to enter lesser value.' , 'random_id': random.randint(0, 100000)})
                except Exception as err:

                    full_stack_trace = traceback.format_exc()
                    answer.update({'message' : 'Oops, there\'s something wrong. Try later.', 'random_id': random.randint(0, 100000)})
                    print("BLIN {}".format(full_stack_trace))
                answers.append(answer)
                break
            line = process.stdout.readline()
            if not line:
                continue
            line_split=line.decode().split(" ")
            #print(line.decode())
            
            if line_split[0]=='center':
                value+=1
                answer.update({'message' : 'Progress: {}/{}'.format(value, cfg.CLUSTERING_N_INIT), 'random_id': random.randint(0, 100000)})
                answers.append(answer)
 
        
def sendMessages(): #MESSAGE SENDER
     timer=time.time()
     message_counter=0
     while True:
        if time.time() - timer < cfg.MESSAGE_SEND_INTERVAL and message_counter < cfg.MESSAGE_N_PER_INTERVAL:
             if answers:
                message_counter+=1
                print(answers)
                vk_session.method('messages.send', answers.popleft())
        elif time.time() - timer >= cfg.MESSAGE_SEND_INTERVAL:
            message_counter=0
            timer=time.time()

def main():
    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(type(event.obj))
            print(event.obj)  # Тут хранится все инфорация о сообщении
            print()

            message = event.obj.message
            peer_id = message['peer_id']  # ID пользователя куда отсылать ответ
            from_id = message['from_id']  # ID пользователя который прислал сообщение
            text = message['text']  # Текст сообщения
            clusters_n=cfg.DEFAULT_N_CLUSTERS
            

            answer = {
                    'peer_id': peer_id,
                    'random_id': random.randint(0, 100000),
            }
                            
            if len(text) > 0: #FINDING CLUSTERS COUNT
                try:
                    clusters_n=int(text)
                except ValueError:
                    clusters_n=cfg.DEFAULT_N_CLUSTERS
                answer.update({'message' : f'{clusters_n} clusters will be found', 'random_id': random.randint(0, 100000)})
                answers.append(answer)
                        

            attachments = message['attachments']  # Вложенные файлы(это и изображения и музыка и видео и т.д)
            print(type(attachments))  # Так как их может быть несколько это список
            print(attachments)
            print()

            if len(attachments) > 0 and attachments[0]['type'] == 'photo': 
                photo = attachments[0]['photo']
                print(type(photo))
                print(photo)
                print()
                photos = sorted(photo['sizes'], key=lambda a: a['height'], reverse=True)
                best_photo = photos[0]
                best_photo_url = best_photo['url']
                thread=Thread(target=start_clustering, args=[clusters_n, best_photo_url, answer])  #PROGRESS HANDLER
                thread.start()

if __name__ == '__main__':
    thread=Thread(target=sendMessages) #MESSAGE SENDER
    thread.start()
    while True:
        try:  # Чтоб не падало
            print("(RE)START")
            main()
        except Exception as err:
        
            full_stack_trace = traceback.format_exc()
            # Возвращяет всю ошибку. Иначе написало бы только последную строку
            print("BLIN {}".format(full_stack_trace))
