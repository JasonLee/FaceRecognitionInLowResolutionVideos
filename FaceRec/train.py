import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from model import FaceNetModel, SiameseNetwork
from dataset import FaceDatasetOrganised, Rescale, ToTensor, FaceDataset
import argparse
import sys
from torch.autograd import Function
from torch.nn.modules.distance import PairwiseDistance

class TripletLoss(nn.Module):
    '''Used to compute triplet loss which is used for training.'''
    def __init__(self, margin = 1):
        super(TripletLoss,self).__init__()
        self.margin= margin

    def forward(self, anchor, positive, negative):
        APDistance = (anchor - positive).pow(2).sum(1)
        ANDistance = (anchor - negative).pow(2).sum(1)
        loss = F.relu(APDistance - ANDistance + self.margin)
        return loss.sum()




def runTrain(args):
    '''Run Training.'''


    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    composed = transforms.Compose([Rescale([224, 224]),ToTensor()])
    #Set up training
    if args.single_directory:
        trainDataset = FaceDataset(csv_file = args.train_list, root_dir = args.image_dir, forTrain = True, transform = composed)
    else:
        trainDataset = FaceDatasetOrganised(root_dir = args.train_dir, forTrain = True, transform = composed)
    trainDataloader = DataLoader(trainDataset, batch_size=args.batch_size, shuffle=True, num_workers=8)
    net = FaceNetModel()
    checkpoint = None
    pre_loss = 0
    pre_lr = args.learning_rate
    if args.resume_training:
        checkpoint = torch.load("./"+args.model_name)
        net.load_state_dict(checkpoint['model_state_dict'])
        net.eval()
    net = net.to(device)
    criterion = TripletLoss()
    optimizer = optim.Adam(net.parameters(), lr=pre_lr)
    if args.resume_training:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    #Training
    for epoch in range(args.epoch):
        torch.save({'model_state_dict': net.state_dict(),'optimizer_state_dict':optimizer.state_dict()}, './'+args.model_name)
        total_loss = 0
        for i, data in enumerate(trainDataloader,0):
            anchor, positive, negative = data
            anchor.to(device)
            positive.to(device)
            negative.to(device)
            anchor_out, positive_out, negative_out = net.forward_triple(anchor, positive, negative)
            optimizer.zero_grad()
            loss = criterion(anchor_out, positive_out, negative_out)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.data.cpu().numpy())
            if i % 500 == 0:
                print('Current loss: %.3f' %(float(loss.data.cpu().numpy())))
        pre_loss += total_loss
        if (args.dynamic_lr and (not epoch == 0) and epoch%int(args.epoch/4) == 0):
            pre_lr /= 4
            optimizer = optim.Adam(net.parameters(),lr = pre_lr)
            pre_loss = 0
        print('Whole dataset trained time: '+str(epoch+1) + ', current loss = '+ str(total_loss))
        print('Current learning rate = '+ str(optimizer.param_groups[0]['lr']))


    print('Training done.')
    #Save the trained model to disk.
    torch.save({'model_state_dict': net.state_dict(), 'optimizer_state_dict': optimizer.state_dict()}, "./"+args.model_name)
