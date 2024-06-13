# conda activate diffusers
from PIL import Image
from torchvision import transforms
import torch
import cv2
import segmentation_models_pytorch as smp
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as T
from tqdm import tqdm

from torchvision import models
import glob

fcn = models.segmentation.fcn_resnet101(pretrained=True).eval()


# Define the helper function
def decode_segmap(image, nc=21):
    label_colors = np.array(
        [
            (255, 255, 255),  # 0=background
            # 1=aeroplane, 2=bicycle, 3=bird, 4=boat, 5=bottle
            (128, 0, 0),
            (0, 128, 0),
            (128, 128, 0),
            (0, 0, 128),
            (128, 0, 128),
            # 6=bus, 7=car, 8=cat, 9=chair, 10=cow
            (0, 128, 128),
            (128, 128, 128),
            (64, 0, 0),
            (192, 0, 0),
            (64, 128, 0),
            # 11=dining table, 12=dog, 13=horse, 14=motorbike, 15=person
            (192, 128, 0),
            (64, 0, 128),
            (192, 0, 128),
            (64, 128, 128),
            (0, 0, 0),
            # 16=potted plant, 17=sheep, 18=sofa, 19=train, 20=tv/monitor
            (0, 64, 0),
            (128, 64, 0),
            (0, 192, 0),
            (128, 192, 0),
            (0, 64, 128),
        ]
    )
    r = np.zeros_like(image).astype(np.uint8)
    g = np.zeros_like(image).astype(np.uint8)
    b = np.zeros_like(image).astype(np.uint8)
    for l in range(0, nc):
        idx = image == l
        r[idx] = label_colors[l, 0]
        g[idx] = label_colors[l, 1]
        b[idx] = label_colors[l, 2]
    rgb = np.stack([r, g, b], axis=2)
    return rgb


def segment(net, img):
    trf = T.Compose(
        [
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    inp = trf(img).unsqueeze(0)
    out = net(inp)["out"]
    om = torch.argmax(out.squeeze(), dim=0).detach().cpu().numpy()
    og_rgb = decode_segmap(om)
    rgb = og_rgb.copy()
    return rgb


dlab = models.segmentation.deeplabv3_resnet101(pretrained=1).eval()
images = sorted(
    glob.glob(
        "/nethome/skareer6/flash9/Projects/EgoPlay/diffusers/data/hand_images/*.png"
    )
)
print("images", images)

for i, image in tqdm(enumerate(images), desc="Images Processed", total=len(images)):
    input_image = cv2.imread(image)
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    rgb = segment(dlab, input_image)
    input_image[rgb == 255] = 0
    input_image[rgb != 255] = 255
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    cv2.imwrite(
        f"/nethome/skareer6/flash9/Projects/EgoPlay/diffusers/data/hand_images/mask_{image.split('/')[-1]}",
        input_image,
    )
