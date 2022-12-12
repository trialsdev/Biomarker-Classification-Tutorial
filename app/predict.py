import torch
import torch.nn as nn
import pretrainedmodels
import ssl
import cv2
from torch.utils.data import DataLoader
from torchvision import transforms
from PIL import Image

import tqdm
import os
import numpy as np
import pandas as pd

from model import model

#load model
model = model()

#get image list
def predict_images(image_dir):

    df = pd.DataFrame(columns = ['ID', 'any', 'epidural', 'intraparenchymal', 'intraventricular', 'subarachnoid', 'subdural'])
    image_list = os.listdir(image_dir)

    for i, image_name in enumerate(image_list):
        
        try:

            image_file = f'data/images/{image_list[i]}'
            image = cv2.imread(image_file)
            image = cv2.resize(image, (256, 256))
            image = cv2.normalize(image, None, 255, 1, cv2.NORM_MINMAX)
            image_tensor = torch.tensor(image)
            im = image_tensor.float()
            im = im.reshape(-1, 256, 256)
            im = im.unsqueeze(0)
            with torch.no_grad():
                inputs = torch.autograd.variable(im)

            feature = model.module.model_ft.layer0(inputs)
            feature = model.module.model_ft.layer1(feature)
            feature = model.module.model_ft.layer2(feature)
            feature = model.module.model_ft.layer3(feature)
            feature = model.module.model_ft.layer4(feature)
            feature = model.module.model_ft.avg_pool(feature)

            feature = feature.view(feature.size(0), -1)

            feature = model.module.model_ft.last_linear(feature)

                        
            feature = feature.sigmoid()

            #get the outputs
            output_probability = feature.data.numpy()
            output_preds = np.where(output_probability > 0.5, 1, 0)
            
            #save predictions in the dataframe
            dict = {
                'ID': image_list[i].split('.')[0],
                'any': output_preds[0][0],
                'epidural': output_preds[0][1],
                'intraparenchymal': output_preds[0][2],
                'intraventricular': output_preds[0][3],
                'subarachnoid': output_preds[0][4],
                'subdural': output_preds[0][5]
            }
            df = df.append(dict, ignore_index = True)

        except Exception as e:
            print(e)

    return df