#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import print_function
import binascii
import struct
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import webcolors
from os import listdir
import os
from os.path import isfile, join
import time
import random
from instabot import Bot
from skimage import measure
import cv2
import pandas as pd
import json
from random import sample
from decouple import config

USER = config('IG_USERNAME')
PASSWORD = config('IG_PASSWORD')

print(USER, PASSWORD)

bot = Bot()
bot.login(username=USER, password=PASSWORD)
bot.like_timeline()


# In[2]:


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


def find_color_clusters(image_path):
    FINAL_COLOURS = []

    NUM_CLUSTERS = 50

    im = Image.open(image_path)
    im = im.resize((100, 100))
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

    index_max = scipy.argmax(counts)                    # find most frequent

    for code in codes:
        colour = binascii.hexlify(bytearray(int(c)
                                            for c in code)).decode('ascii')
        rgb_colour = tuple(int(colour[i:i+2], 16) for i in (0, 2, 4))
        final = get_colour_name(rgb_colour)
        FINAL_COLOURS.append(final[1])

    counts = dict()
    for i in FINAL_COLOURS:
        counts[i] = counts.get(i, 0) + 1
    return counts


# In[3]:


print("🌱 Creating image lists")

pestofreaks_images = './pestofreaks'
posted_images = ['./pestofreaks/'+f for f in listdir(
    pestofreaks_images) if isfile(join(pestofreaks_images, f))]

folders = ['./pesto',
           './pastapesto',
           './pestosauce',
           './gnocchialpesto',
           './pestogenovese',
           './trofiealpesto',
           './pestopasta',
           './pestofresco',
           './pestoallagenovese',
           './pastaalpesto',
           './pestoalpesto',
           './pestoligure', ]


# In[4]:


images = []
for i in folders:
    fileimages = [i+'/'+f for f in listdir(i) if isfile(join(i, f))]
    images = images + fileimages


# In[11]:


for image in images:
    if '.json' in image:
        images.remove(image)


# In[5]:


# REMOVE VIDEOS
print("🌱 Removing mp4s")
for image in images:
    if '.mp4' in image:
        images.remove(image)


# In[38]:


# REMOVE POSTED IMAGES
print("🌱 Removing posted images")
l = []
for post in images:
    for posted in posted_images:
        try:
            image1 = cv2.imread(post)
            image1 = cv2.resize(image1, (100, 100))

            image2 = cv2.imread(posted)
            image2 = cv2.resize(image2, (100, 100))

            s = measure.compare_ssim(image1, image2, multichannel=True)
            l.append([s, post, posted])
        except:
            next

df = pd.DataFrame(l, columns=['sim', 'to_post', 'posted'])
remove = list(df[df['sim'] > 0.7]['to_post'])
l3 = [x for x in list(df['to_post']) if x not in remove]
images_to_post = list(set(l3))


# In[41]:


post_images = []
print("🌱 Color coding images")
for image in images_to_post:
    colours = find_color_clusters(image)
    colours_filtered = {k: v for k, v in colours.items() if v >= 5}
    GREENS = ['lawngreen', 'chartreuse', 'limegreen', 'lime', 'forestgreen', 'green', 'darkgreen', 'greenyellow', 'yellowgreen',
              'lightgreen', 'palegreen', 'darkseagreen', 'mediumseagreen', 'lightseagreen', 'seagreen', 'olive', 'olivedrab']
    for c in colours_filtered:
        if c in GREENS:
            post_images.append(image)
            next

post_images = list(set(post_images))
print(f"🌱 Can post {len(post_images)}")

# In[42]:


# for i in post_images:
#     im = Image.open(i)
#     im = im.resize((300, 300))
#     im.show()


# In[63]:


image_user = []

for num in range(0, len(folders)):
    path = folders[num]+'/'+folders[num].split('/')[1]+'.json'

    with open(path) as f:
        d = json.load(f)

    for details in d['GraphImages']:
        try:
            try:
                image_url = details['display_url'].split('/')[7].split('?')[0]
                user = details['owner']['id']
                image_user.append([image_url, user])
            except:
                image_url = details['display_url'].split('/')[6].split('?')[0]
                user = details['owner']['id']
                image_user.append([image_url, user])
        except:
            next


# In[64]:


post_w_details = []
for i in post_images:
    for d in image_user:
        if(d[0] == i.split('/')[2]):
            post_w_details.append([i, bot.get_username_from_user_id(d[1])])

try:
    post_w_details_short = sample(post_w_details, random.randint(3, 7))
except:
    post_w_details_short = sample(post_w_details, 2)

# In[58]:

print(f"🌱 Posting {len(post_w_details_short)} images")
c = 0
for post in post_w_details_short:
    time.sleep(random.randint(1, 10))
    x = post[1]

    captions = [
        f'Amazing pesto! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Send us your recipes! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'This is such a beautiful dish! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Send pesto! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'May the Pesto be with you! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'We cant resist! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Wow! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Wow! Piatto fantastico da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto fantastico da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto meraviglioso, piatto gustosissimo da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Gran piatto da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Sembra un piatto fantastico! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Postiamo solo i piatti migliori! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Viva la pasta al pesto! 💚 Post by @{x} #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Post by @{x} 💚🌱 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Post by @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Post by @{x} 💚🌱 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Post by @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto da @{x} 💚🌱 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto da @{x} 💚🌱 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto da @{x} 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',
        f'Piatto da @{x} 💚🌱 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #pasta #foodblog #foodlovers #foodie #foodporn #foodpics',


    ]

    try:

        bot.upload_photo(
            post[0],
            caption=random.choice(captions).strip(),
            options={"rename": False},
        )
    except:
        c = c+1
        next

print(f"There were {c} error uploading")
print("🌱 Getting quote")

quote_to_post = ['./quotes'+"/" +
                 f for f in listdir('./quotes') if isfile(join('./quotes', f))]

for q in quote_to_post:
    if '.DS' in q:
        quote_to_post.remove(q)

quote = random.choice(quote_to_post)
bot.upload_photo(
    quote,
    caption="Send us your amazing dishes! 💚 #pestofreaks #pesto #pastapesto #pestolovers #pestosauce #italy #italian #food #repost",
    options={"rename": False},
)

os.remove(quote)


print("🌱 Clean up")
