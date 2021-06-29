#!/usr/bin/env python
# -*- coding: utf-8 -*-

import websockets
import json
import asyncio
from utils import convert_data
import datetime
from config_logger import *
from additional_data import *


market_asks = {}
market_bids = {}

best_ask = {}
best_bid = {}

async def init_default_data():
    global best_ask
    global best_bid
    
    for item in payload_data_best_ask_and_bid:
        name_pair = item['name']
        best_ask[name_pair] = 0
        best_bid[name_pair] = 0

async def update_market_price_incremental(data):
    url = data['url']
    payload_data = data['payload']
    name_pair = data['name']

    global market_asks
    global market_bids

    async with websockets.connect(url) as client:

        send_peyload_data = False
        while True:
            received_raw_data = await client.recv()
            data = convert_data(received_raw_data)
            ping_timestamp = 0
            try:
                ping_timestamp = int(data['ping'])
            except: pass

            try:
                logger.debug('New data: asks[%s], bids: [%s]' % (len(data['tick']['asks']), len(data['tick']['bids'])))
            except:
                logger.debug('Response error: get data >> %s' % (data))

            not_in_global_asks = 0
            in_global_asks = 0
            
            not_in_global_bids = 0
            in_global_bids = 0
            
            try:
                for ask in data['tick']['asks']:
                    if ask not in market_asks[name_pair]:
                        not_in_global_asks += 1
                        list_asks = market_asks.get(name_pair)
                        list_asks.append(bid)
                    elif ask in market_asks[name_pair]:
                        in_global_asks += 1
                        list_asks = market_asks.get(name_pair)
                        list_asks.remove(ask)
            except:
                logger.debug('Error incremental bids')

            try:
                for bid in data['tick']['bids']:
                    if bid not in market_bids[name_pair]:
                        not_in_global_bids += 1
                        list_bids = market_bids.get(name_pair)
                        list_bids.remove(bid)
                    elif bid in market_bids[name_pair]:
                        in_global_bids += 1
                        list_bids = market_bids.get(name_pair)
                        list_bids.remove(bid)
            except:
                logger.debug('Error incremental asks')

            
            if ping_timestamp > 0 :
                # check server send message ping
                message = json.dumps({"pong": ping_timestamp})
                # and send response pong
                await client.send(message)
                
            if ping_timestamp > 0 and send_peyload_data == False:
                message = json.dumps(payload_data)
                # send payload data
                await client.send(message)
                send_peyload_data = True


            # print in console
            try:
                logger.debug('New Asks: Add [%s] - Delete [%s] = Diff [%s]' % (not_in_global_asks, in_global_asks, str(not_in_global_asks-in_global_asks)))
                logger.debug('New Bids: Add [%s] - Delete [%s] = Diff [%s]' % (not_in_global_bids, in_global_bids, str(not_in_global_bids-in_global_bids)))
                logger.info('Global %s: asks [%s] - bids [%s]' % (name_pair ,len(market_asks[name_pair]), len(market_bids[name_pair])))
            except:
                pass


async def get_market_depth_data(data):
    url = data['url']
    payload_data = data['payload']
    name_pair = data['name']
    
    send_peyload_data = False
    
    async with websockets.connect(url) as client:
        is_data_come = False
        
        while is_data_come == False:
            received_raw_data = await client.recv()
            data = convert_data(received_raw_data)
            ping_timestamp = 0
            
            try:
                ping_timestamp = int(data['ping'])
            except: pass
        
            try:
                logger.debug('Market Depth - bids: %s , asks: %s' % (len(data['tick']['bids']), len(data['tick']['asks'])))
                global market_bids
                global market_asks
                market_bids[name_pair] = data['tick']['bids']
                market_asks[name_pair] = data['tick']['asks']

                if len(market_asks) == 150 and len(market_bids) == 150:
                    is_data_come = True
            except:
                logger.debug('Error in get market depth data')
            
            if ping_timestamp > 0 :
                # check server send message ping
                message = json.dumps({"pong": ping_timestamp})
                # and selfend response pong
                await client.send(message)
            
            if ping_timestamp > 0 and send_peyload_data == False:
                message = json.dumps(payload_data)
                # send payload data
                await client.send(message)
                send_peyload_data = True

                
async def get_best_ask_and_bid(data):
    url = data['url']
    payload_data = data['payload']
    name_pair = data['name']
    send_peyload_data = False
    
    async with websockets.connect(url) as client:
        while True:
            received_raw_data = await client.recv()
            data = convert_data(received_raw_data)
            ping_timestamp = 0
            
            try:
                ping_timestamp = int(data['ping'])
            except: pass

            global best_ask
            global best_bid

            try:
                best_ask[name_pair] = data['tick']['ask']
                best_bid[name_pair] = data['tick']['bid']
            except: pass
                
            if ping_timestamp > 0 :
                # check server send message ping
                message = json.dumps({"pong": ping_timestamp})
                # and selfend response pong
                await client.send(message)
            
            if ping_timestamp > 0 and send_peyload_data == False:
                message = json.dumps(payload_data)
                # send payload data
                await client.send(message)
                send_peyload_data = True


async def print_best_ask_and_bid(data):
    name_pair = data['name']
    
    while True:
        global best_ask
        global best_bid

        try: 
            logger.info('Best %s: ask - %s, bid - %s ' % (name_pair, best_ask[name_pair], best_bid[name_pair]))
            await asyncio.sleep(5)
        except:
            pass

async def empty():
    await asyncio.sleep(100000)

async def bot():
    loop.create_task(init_default_data())
    for data in payload_data_best_ask_and_bid:
        loop.create_task(get_best_ask_and_bid(data))
        loop.create_task(print_best_ask_and_bid(data))
    for data in payload_data_market_depth:
        loop.create_task(get_market_depth_data(data))

    for data in payload_data_market_price:
        loop.create_task(update_market_price_incremental(data))
    await empty()

loop = asyncio.get_event_loop()
loop.run_until_complete(bot())
