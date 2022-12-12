import torch
import torch.nn as nn
import pretrainedmodels
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class se_resnext50_32x4d(nn.Module):
    def __init__(self):
        super(se_resnext50_32x4d, self).__init__()
        self.model_ft = pretrainedmodels.__dict__['se_resnext50_32x4d'](num_classes=1000, pretrained='imagenet')
        num_ftrs = self.model_ft.last_linear.in_features
        self.model_ft.avg_pool = nn.AdaptiveAvgPool2d((1,1))
        self.model_ft.last_linear = nn.Sequential(nn.Linear(num_ftrs, 6, bias=True))

    def forward(self, x):
        x = self.model_ft(x)
        return 

#load model
def model():

    model = eval('se_resnext50_32x4d()')
    model = nn.DataParallel(model)

    state = torch.load('weights/model_epoch_best_4.pth', map_location = 'cpu')

    model.load_state_dict(state['state_dict'], strict = False)

    return model

if __name__ == "__main__":

    model()