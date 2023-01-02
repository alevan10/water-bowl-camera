import asyncio

from waterbowl.run_waterbowl_watcher import watch_water_bowl

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(watch_water_bowl())
