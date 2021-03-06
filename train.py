import yaml
from helpers import read_directory_images, resize_images
from descriptors import *
from svm import *
from sklearn.externals import joblib
from ast import literal_eval


def load_descriptor(settings):
    return {
        'hog': HogDescriptor.from_config_file(settings['hog']),
        'lbp': LBPDescriptor.from_config_file(settings['lbp']),
        'haar': HaarDescriptor.from_config_file(settings['haar'])
    }.get(settings['train']['descriptor'], 'hog')    # Default to HOG for invalid input


if __name__ == "__main__":

    with open("config.yaml", "r") as stream:
        settings = yaml.load(stream)

    descriptor = load_descriptor(settings)
    classifier = SVM(descriptor, settings['svm']['C'])

    print("Descriptor Settings \n" + str(descriptor))
    print("Classifier Settings \n" + str(classifier))
    print("Reading in the images...")

    positive_images = read_directory_images(settings['train']['positive_image_directory'], extension='.png')
    negative_images = read_directory_images(settings['train']['negative_image_directory'], extension='.png')

    training_size = literal_eval(settings['train']['window_size'])
    positive_images = resize_images(list(positive_images), training_size)
    negative_images = resize_images(list(negative_images), training_size)
    images = np.concatenate((positive_images, negative_images))

    # LBP and Haar-like descriptors require gray images
    if settings['train']['descriptor'] != 'hog':
        images = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in images]

    # Set up the labels for binary classification
    labels = np.array([1] * len(positive_images) + [0] * len(negative_images))

    print("Starting training...")
    classifier.train(images, labels)
    joblib.dump(classifier, settings['train']['outfile'])
