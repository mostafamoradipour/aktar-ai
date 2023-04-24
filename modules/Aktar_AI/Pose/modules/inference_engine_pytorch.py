import numpy as np
import torch


class InferenceEnginePyTorch:
    def __init__(self, checkpoint_path, device,
                 img_mean=np.array([128, 128, 128], dtype=np.float32),
                 img_scale=np.float32(1/255)):
        from modules.Aktar_AI.Pose.models.with_mobilenet import PoseEstimationWithMobileNet
        from .load_state import load_state
        self.img_mean = img_mean
        self.img_scale = img_scale
        self.device = 'cpu'
        if device != 'CPU':
            if torch.cuda.is_available():
                self.device = torch.device('cuda:0')
            else:
                print('No CUDA device found, inferring on CPU')

        net = PoseEstimationWithMobileNet()
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        load_state(net, checkpoint)
        net = net.to(self.device)
        net.eval()
        self.net = net

    def infer(self, imgs):
        data = []
        for img in imgs:
            normalized_img = InferenceEnginePyTorch._normalize(img, self.img_mean, self.img_scale)
            data.append(torch.from_numpy(normalized_img).permute(2, 0, 1))
        data = torch.stack(data).to(self.device)
        # print(type(data), data.shape)
        # print(data)
        heatmaps, pafs = self.net(data)
        # print(features[-1].squeeze().data.cpu().numpy().shape)
        # print(heatmaps[-1].squeeze().data.cpu().numpy().shape)
        # print(pafs[-1].squeeze().data.cpu().numpy().shape)
        # print('----')
        # print(features)
        # print(features[-1].shape)
        # print(features[-1].squeeze().shape)
        return (heatmaps.data.cpu().numpy(), pafs.data.cpu().numpy())

    @staticmethod
    def _normalize(img, img_mean, img_scale):
        normalized_img = (img.astype(np.float32) - img_mean) * img_scale
        return normalized_img
