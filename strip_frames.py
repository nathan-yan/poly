from PIL import Image
import matplotlib.pyplot as plt

import numpy as np

plt.ion()

im = Image.open("ezgif.com-crop (1).gif")

for j in range (1):
    for i in range (18):       # TO GET WALK FRAMES
        im.seek(12 + i)

    #for i in range (10):
    #    im.seek(i)
        im.save("frames/player_walk_frame%s.png" % i)

        #frame = np.array(im.getdata()).reshape([46, 74])

        #print(frame.shape)

        #plt.clf()

        #plt.imshow(frame)
        #plt.pause(0.5)

#im.save("frame0.png")