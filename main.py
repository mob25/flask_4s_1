import argparse
import asyncio
import multiprocessing
import os
import threading
import time
from pathlib import Path

import requests

image_urls = []
with open('links.txt', 'r') as images:
    for image in images.readlines():
        image_urls.append(image.strip())

if not os.path.isdir("images"):
    os.mkdir("images")


def download_image(url):
    image_path = Path('images')
    start_time = time.time()
    response = requests.get(url, stream=True).content
    filename = image_path.joinpath(os.path.basename(url))
    f = open(filename, 'wb')
    f.write(response)
    f.close()
    end_time = time.time() - start_time
    print(f"Загрузка {filename} - {end_time:.2f} секунд")
    return end_time


async def download_image_async(url):
    image_path = Path('images')
    start_time = time.time()
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"stream": True})
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Загрузка {filename} - {end_time:.2f} секунд")


def download_images_synhr(urls):
    end_time = 0
    for url in urls:
        end_time += download_image(url)
    print(f"Общее время при синхронном подходе: {end_time:.2f} сек.\n")
    return end_time


def download_images_threading(urls):
    start_time = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time() - start_time
    print(f"Общее время при многопоточном подходе: {end_time:.2f} сек.\n")
    return end_time


def download_images_multiprocessing(urls):
    start_time = time.time()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    end_time = time.time() - start_time
    print(f"Общее время при мультипроцессорном подходе: {end_time:.2f} сек.\n")
    return end_time


async def download_images_asyncio(urls):
    start_time = time.time()
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download_image_async(url))
        tasks.append(task)
    await asyncio.gather(*tasks)
    end_time = time.time() - start_time
    print(f"Общее время при асинхронном подходе - {end_time:.2f} сек.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка фото")
    parser.add_argument("--urls", nargs="+")
    args = parser.parse_args()
    urls = args.urls
    if not urls:
        urls = image_urls

# python main.py --urls https://mob25.com/wp-content/uploads/2024/06/70796410.jpg https://mob25.com/wp-content/uploads/2024/06/70760521.jpg https://mob25.com/wp-content/uploads/2024/06/70784458.jpg

    print(f"Загрузка в синхронном режиме")
    endtime_synhr = download_images_synhr(urls)

    print(f"Загрузка в многопоточном режиме")
    endtime_thread = download_images_threading(urls)

    print(f"Загрузка в многопроцессорном режиме")
    end_time_procces = download_images_multiprocessing(urls)

    print(f"загрузка в асинхронном режиме")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(download_images_asyncio(urls))