import argparse
import os

import pandas as pd
import PIL
import torch
import torchvision.transforms as transforms
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision.utils import save_image
from tqdm import trange

from datasets import ImageDataset
from feature_extractor import FeatureExtractor
from model import Generator, Discriminator

# Stops recursively creating in windows
if __name__ == '__main__':

    # Creates folder to save training result samples
    os.makedirs('samples', exist_ok=True)

    # Create folder to save generator models
    os.makedirs('models', exist_ok=True)

    # Create folder to save model to continue training
    os.makedirs('training_models', exist_ok=True)

    # Create folder to save loss values
    os.makedirs('training_data', exist_ok=True)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train SRGAN')
    parser.add_argument('--upscale_factor', default=4, type=int, choices=[2, 4, 8],
                        help='super resolution upscale factor')
    parser.add_argument('--epoch_start', default=0, type=int, help='epoch to start at')
    parser.add_argument('--num_epochs', default=200, type=int, help='train epoch number')
    parser.add_argument('--disable_bar', default=False, type=bool, help='show tqdm progress bar')
    parser.add_argument('--learning_rate', default=0.0001, type=int, help='learning rate for gen and discrim')
    parser.add_argument('--batch_size', default=16, type=int, help='batch size')
    parser.add_argument('--sample_interval', default=6000, type=int, help='after how many batches print a sample image')
    parser.add_argument('--epoch_checkpoint', default=1, type=int, help='after how many epoch to save models')

    opt = parser.parse_args()

    # set constants
    EPOCH_START = opt.epoch_start
    UPSCALE_FACTOR = opt.upscale_factor
    NUM_EPOCHS = opt.num_epochs
    IMG_HEIGHT = 256
    IMG_WIDTH = 256
    CHANNELS = 3
    BATCH_SIZE = opt.batch_size

    # Saves sample images of training
    SAMPLE_INTERVAL = opt.sample_interval
    # At each interval saves models/training models
    EPOCH_CHECKPOINT = opt.epoch_checkpoint

    # IMAGE_DIRECTORY
    IMAGE_DIRECTORY = 'img_align_celeba/'
    # VALIDATION_IMAGE_DIRECTORY = '/img_align_celeba/'
    DISABLE_BAR = opt.disable_bar
    LEARNING_RATE = opt.learning_rate

    # Creates tensors for low resolution and high resolution images
    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.Tensor
    input_lr = Tensor(BATCH_SIZE, CHANNELS, IMG_HEIGHT // UPSCALE_FACTOR, IMG_WIDTH // UPSCALE_FACTOR)
    input_hr = Tensor(BATCH_SIZE, CHANNELS, IMG_HEIGHT, IMG_WIDTH)

    # Transformations for low resolution images and high resolution images
    lr_transforms = [transforms.Resize((IMG_HEIGHT // UPSCALE_FACTOR, IMG_WIDTH // UPSCALE_FACTOR), PIL.Image.BICUBIC),
                     transforms.ToTensor(),
                     transforms.Normalize((0, 0, 0), (1, 1, 1))]

    hr_transforms = [transforms.Resize((IMG_HEIGHT, IMG_WIDTH), PIL.Image.BICUBIC),
                     transforms.ToTensor(),
                     transforms.Normalize((-1, -1, -1), (1, 1, 1))]

    # Load datasets and separates them into batches
    training_dataloader = DataLoader(
        ImageDataset(IMAGE_DIRECTORY, lr_transforms=lr_transforms, hr_transforms=hr_transforms),
        batch_size=BATCH_SIZE, shuffle=True, num_workers=4, drop_last=True)

    # validation_dataloader = DataLoader(
    #    ImageDataset(VALIDATION_IMAGE_DIRECTORY, lr_transforms=lr_transforms, hr_transforms=hr_transforms),
    #    batch_size=BATCH_SIZE, shuffle=True, num_workers=4, drop_last=True)

    # Initialise Generator and Discriminator
    generator = Generator(UPSCALE_FACTOR)
    discriminator = Discriminator()
    feature_extractor = FeatureExtractor()

    # Adam optimisations for the generators and discriminators
    optimizerG = torch.optim.Adam(generator.parameters(), lr=LEARNING_RATE)
    optimizerD = torch.optim.Adam(discriminator.parameters(), lr=LEARNING_RATE)

    # Losses
    mse_loss = torch.nn.MSELoss()
    bce_loss = torch.nn.BCELoss()

    # One sided label smoothing and parameter for BCELoss
    f = torch.zeros(BATCH_SIZE, 1)
    fake = Variable(f.clone())

    # Use GPU if available
    if torch.cuda.is_available():
        generator = generator.cuda()
        discriminator = discriminator.cuda()
        feature_extractor = feature_extractor.cuda()
        mse_loss = mse_loss.cuda()
        bce_loss = bce_loss.cuda()
        fake = fake.cuda()
        print('CUDA is available')

    # when GPU is not available
    else:
        print('No CUDA')

    # if some epochs have already been trained, then run this code to load everything that
    # has been trained already and that has been saved to a checkpoint
    if EPOCH_START != 0:
        checkpoint = torch.load('training_models/model_%d.pth' % EPOCH_START, map_location='cpu')
        generator.load_state_dict(checkpoint['generator_state_dict'])
        discriminator.load_state_dict(checkpoint['discriminator_state_dict'])
        optimizerG.load_state_dict(checkpoint['optimizerG_state_dict'])
        optimizerD.load_state_dict(checkpoint['optimizerD_state_dict'])
        del checkpoint
        torch.cuda.empty_cache()

    overall_results = {'d_loss': [], 'cont_loss': [], 'adv_loss': [], 'g_loss': []}

    # How many iterations of data-set
    for epoch in range(NUM_EPOCHS):
        epoch += EPOCH_START
        with trange(len(training_dataloader), disable=DISABLE_BAR) as t:  # Progress bar

            # Results to save current epoch data
            running_results = {'d_loss': 0, 'cont_loss': 0, 'adv_loss': 0, 'g_loss': 0}

            # Images in data set
            for i, images in enumerate(training_dataloader):
                batch_size = len(training_dataloader)

                # Configure model input
                imgs_lr = Variable(input_lr.copy_(images['lr']), requires_grad=False)
                imgs_hr = Variable(input_hr.copy_(images['hr']), requires_grad=False)

                if torch.cuda.is_available():
                    imgs_lr = imgs_lr.cuda()
                    imgs_hr = imgs_hr.cuda()

                # UPDATING THE DISCRIMINATOR:

                discriminator.zero_grad()
                real_out = discriminator(imgs_hr)
                gen_hr_fake = generator(imgs_lr)
                dis_gen_hr_fake = discriminator(gen_hr_fake)

                # Adversarial ground truths
                # One sided label smoothing
                v = torch.rand(real_out.size()) * 0.15 + 0.85

                valid = Variable(v.clone().detach())

                if torch.cuda.is_available():
                    valid = valid.cuda()

                # Typical GAN discriminator
                discriminator_loss = bce_loss(real_out, valid) + bce_loss(dis_gen_hr_fake, fake)

                del valid

                discriminator_loss.backward(retain_graph=True)
                optimizerD.step()

                # UPDATING THE GENERATOR:
                generator.zero_grad()

                generator_features_ghf = feature_extractor(gen_hr_fake)

                # Pass high res image into VGG feature extractor
                real_features_hr = Variable(feature_extractor(imgs_hr).data)

                content_loss = mse_loss(real_features_hr, generator_features_ghf)

                adversary_loss = bce_loss(dis_gen_hr_fake, torch.ones_like(dis_gen_hr_fake))

                # SRGAN Generator Loss
                loss_GAN = content_loss + 1e-3 * adversary_loss
                loss_GAN.backward()

                optimizerG.step()

                # UPDATE PROGRESS BAR WITH INFO
                running_results['g_loss'] = loss_GAN.item()
                running_results['d_loss'] = discriminator_loss.item()
                running_results['adv_loss'] = adversary_loss.item()
                running_results['cont_loss'] = content_loss.item()

                # Updates progress bar
                if not DISABLE_BAR:
                    t.set_description(desc='[%d/%d] | Loss_D: %.4f | Adv_Loss: %.4f | Cont_Loss: %.4f | Loss_G: %.4f'
                                           % (
                                               epoch, NUM_EPOCHS, running_results['d_loss'],
                                               running_results['adv_loss'],
                                               running_results['cont_loss'],
                                               running_results['g_loss']))
                    t.update()

                # Saves sample images
                batches_done = epoch * len(training_dataloader) + i
                if batches_done % SAMPLE_INTERVAL == 0:
                    # Upscale image to same tensor size
                    bilinear_low_res = torch.nn.functional.interpolate(imgs_lr.data, size=(256, 256), mode='bilinear',
                                                                       align_corners=False)
                    # Save images as png file into folder
                    save_image(torch.cat((bilinear_low_res, gen_hr_fake.data, imgs_hr.data), -2),
                               'samples/%d.png' % batches_done, normalize=True)

                del imgs_lr, imgs_hr, real_features_hr

            # If progress bar is disabled then print loss values to console
            if DISABLE_BAR:
                print('[%d/%d] | Loss_D: %.4f | Adv_Loss: %.4f | Cont_Loss: %.4f | Loss_G: %.4f'
                      % (
                          epoch,
                          NUM_EPOCHS,
                          running_results['d_loss'],
                          running_results['adv_loss'],
                          running_results['cont_loss'],
                          running_results['g_loss']))

            overall_results['d_loss'].append(running_results['d_loss'])
            overall_results['g_loss'].append(running_results['g_loss'])
            overall_results['adv_loss'].append(running_results['adv_loss'])
            overall_results['cont_loss'].append(running_results['cont_loss'])

            # Save model parameters and saves it to a checkpoint, so that it can be loaded again
            if epoch % EPOCH_CHECKPOINT == 0:
                torch.save(generator.state_dict(), 'models/generator_%d.pth' % epoch)
                torch.save({
                    'epoch': epoch,
                    'generator_state_dict': generator.state_dict(),
                    'discriminator_state_dict': discriminator.state_dict(),
                    'optimizerG_state_dict': optimizerG.state_dict(),
                    'optimizerD_state_dict': optimizerD.state_dict()
                }, 'training_models/model_%d.pth' % epoch)

                # Saves data into a csv file.
                df = pd.DataFrame(
                    data={'Loss_D': overall_results['d_loss'],
                          'Loss_G': overall_results['g_loss'],
                          'Adv_Loss': overall_results['adv_loss'],
                          'Cont_Loss': overall_results['cont_loss']},
                    index=range(EPOCH_START, epoch + 1))
                df.to_csv('training_data/training_results.csv', index_label='Epoch')



