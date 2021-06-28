#!/usr/bin/env python
# -*- coding: utf-8 -*-

import websockets
import json
import asyncio
from utils import convert_data

market_bids = []
market_asks = []


async def update_market_price_incremental():
    url = 'wss://api.huobi.pro/ws'
    payload_data = {
        "sub": "market.btcusdt.mbp.refresh.20",
        "id": "id1"
    }

    global market_asks
    global market_bids

    async with websockets.connect(url) as client:

        while True:
            received_raw_data = await client.recv()
            data = convert_data(received_raw_data)
            ping_timestamp = 0
            try:
                ping_timestamp = int(data['ping'])
            except: pass

            try:
                print('New data: asks[%s], bids: [%s]' % (len(data['tick']['asks']), len(data['tick']['bids'])))
            except:
                print('Response error: get data >> %s' % (data))

            not_in_global_asks = 0
            in_global_asks = 0
            
            not_in_global_bids = 0
            in_global_bids = 0
            
            try:
                for bid in data['tick']['bids']:
                    if bid not in market_bids:
                        not_in_global_bids += 1
                        market_bids.append(bid)
                    elif bid in market_bids:
                        in_global_bids += 1
                        market_bids.remove(bid)
            except:
                print('Error incremental bids')

            try:
                for ask in data['tick']['asks']:
                    if ask not in market_asks:
                        not_in_global_asks += 1
                        market_asks.append(ask)
                    elif ask in market_asks:
                        in_global_asks += 1
                        market_asks.remove(ask)
            except:
                print('Error incremental asks')

            
            if ping_timestamp > 0 :
                # check server send message ping
                message = json.dumps({"pong": ping_timestamp})
                # and send response pong
                await client.send(message)
                
            if ping_timestamp > 0 :
                message = json.dumps(payload_data)
                # send payload data
                await client.send(message)


            # print in console
            try: 
                print('New Asks: Add [%s] - Delete [%s] = Diff [%s]' % (not_in_global_asks, in_global_asks, str(not_in_global_asks-in_global_asks)))
                print('New Bids: Add [%s] - Delete [%s] = Diff [%s]' % (not_in_global_bids, in_global_bids, str(not_in_global_bids-in_global_bids)))
                print('Global: asks [%s] - bids [%s]' % (len(market_asks), len(market_bids)))
            except:
                pass
            print('-'*30)


async def get_market_depth_data():
    
    market_depth_url = 'wss://api.huobi.pro/ws'
    payload_data = {
        "sub": "market.btcusdt.depth.step0",
        "id": "id1"
    }
    
    async with websockets.connect(market_depth_url) as client:
        is_data_come = False
        
        while is_data_come == False:
            received_raw_data = await client.recv()
            data = convert_data(received_raw_data)
            ping_timestamp = 0
            
            try:
                ping_timestamp = int(data['ping'])
            except: pass
        
            try:
                print('Market Depth - bids: %s , asks: %s' % (len(data['tick']['bids']), len(data['tick']['asks'])))
                global market_bids
                global market_asks
                market_bids = data['tick']['bids']
                market_asks = data['tick']['asks']

                if len(market_asks) == 150 and len(market_bids) == 150:
                    is_data_come = True
            except:
                print('Error in get market depth data')
            
            if ping_timestamp > 0 :
                # check server send message ping
                message = json.dumps({"pong": ping_timestamp})
                # and selfend response pong
                await client.send(message)
            
            if ping_timestamp > 0 :
                message = json.dumps(payload_data)
                # send payload data
                await client.send(message)



async def bot():
    # get 150 items in glass
    loop.create_task(get_market_depth_data())
    await update_market_price_incremental()

loop = asyncio.get_event_loop()
loop.run_until_complete(bot())
