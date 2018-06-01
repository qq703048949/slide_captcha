# -*- coding:utf-8 -*-

from PIL import Image,ImageChops,ImageFilter
import copy



#https://github.com/MashiMaroLjc/Learn-to-identify-similar-images/blob/master/Chinese.md
#计算直方图对比相似度
def calculate(image1, image2):
    g = image1.histogram()
    s = image2.histogram()
    assert len(g) == len(s), "error"

    data = []

    for index in range(0, len(g)):
        if g[index] != s[index]:
            data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
        else:
            data.append(1)

    return sum(data) / len(g)


def split_image(image, part_size):
    pw, ph = part_size
    w, h = image.size

    sub_image_list = []

    assert w % pw == h % ph == 0, "error"

    for i in range(0, w, pw):
        for j in range(0, h, ph):
            sub_image = image.crop((i, j, i + pw, j + ph)).copy()
            sub_image_list.append(sub_image)

    return sub_image_list


def classfiy_histogram_with_split(image1, image2, size=(256, 256), part_size=(64, 64)):
    '''
     'image1' 和 'image2' 都是Image 对象.
     可以通过'Image.open(path)'进行创建。
     'size' 重新将 image 对象的尺寸进行重置，默认大小为256 * 256 .
     'part_size' 定义了分割图片的大小.默认大小为64*64 .
     返回值是 'image1' 和 'image2'对比后的相似度，相似度越高，图片越接近，达到100.0说明图片完全相同。
    '''
    img1 = image1.resize(size).convert("RGB")
    sub_image1 = split_image(img1, part_size)

    img2 = image2.resize(size).convert("RGB")
    sub_image2 = split_image(img2, part_size)

    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)

    x = size[0] / part_size[0]
    y = size[1] / part_size[1]

    pre = round((sub_data / (x * y)), 6)
    #print(pre * 100)
    return pre * 100



def get_offset(bigpath,puzzlepath):
    img_big = Image.open(bigpath).resize((300,169),Image.ANTIALIAS).convert("RGBA")
    img_puzzle = Image.open(puzzlepath).resize((60,169),Image.ANTIALIAS).convert("RGBA").filter(ImageFilter.EDGE_ENHANCE) #接近纯色的块 用边界增强提高成功率
    bw,bh = img_big.size
    pw,ph = img_puzzle.size

    l = []

    for i in range(0,bw - pw):
        #裁剪pluzzle大小
        img_cut = img_big.crop((i,0,i + pw,ph))
        img_copycut = copy.deepcopy(img_cut)
        #抠出阴影块再贴回裁剪图进行对比
        img_darker = ImageChops.darker(img_cut,img_puzzle)
        r,g,b,a = img_darker.split()
        img_copycut.paste(img_darker,mask=a)
        pre = classfiy_histogram_with_split(img_cut,img_copycut,(pw,ph),(pw,ph))
        #相似度100直接返回，否则全部对比完返回最大值索引
        if pre == 100: 
            return i
        l.append(pre)
        #img_cut.save("c:/test/%s-a.png" % i)
        #img_copycut.save("c:/test/%s-b.png" % i)

    print("滑动距离：%s" % (l.index(max(l))))
    return l.index(max(l))

if __name__ == "__main__":
    print(get_offset('ee31296e5ca349b48b8b2420ddcff2ca_big.jpg','ee31296e5ca349b48b8b2420ddcff2ca_puzzle.jpg'))

