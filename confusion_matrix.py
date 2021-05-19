import numpy as np
import matplotlib.pyplot as plt

# from sklearn import svm, datasets
# from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
import itertools



def plot_confusion_matrix(cm):

    plt.figure(figsize=(12, 10))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion matrix')
    plt.colorbar()

    thresh = cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, "{:,}".format(cm[i, j]),
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black")
    plt.xticks(range(cm.shape[0]))
    plt.yticks(range(cm.shape[0]))
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return
    
# cm = np.array([[ 976,    0,    0,    0,    0,    0,    1,    1,    2,    0],
#  [   0, 1135,    0,    0,    0,    0,    0,    0,    0,    0],
#  [   3,    3, 1021,    0,    1,    0,    0,    3,    1,    0],
#  [   3,    0,    1,  991,    0,   10,    0,    2,    2,    1],
#  [   0,    0,    1,    0,  979,    0,    1,    0,    1,    0],
#  [   2,    0,    0,    2,    0,  886,    1,    1,    0,    0],
#  [   2,    3,    0,    1,    1,    4,  947,    0,    0,    0],
#  [   1,    7,    4,    1,    0,    0,    0, 1013,    1,    1],
#  [   4,    2,    2,    0,    1,    2,    0,    2,  957,    4],
#  [   3,    5,    1,    1,    8,    4,    0,    4,    0,  983]])

# plot_confusion_matrix(cm)