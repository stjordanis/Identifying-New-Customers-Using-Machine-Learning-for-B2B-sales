from adaptivePuLearning import AdaPULearning
from sklearn.svm import SVC
from sklearn.datasets import make_classification
import numpy as np

if __name__ == '__main__':
    X, y = make_classification(n_samples=3000,
                               n_features=20,
                               n_informative=2,
                               n_redundant=2,
                               n_repeated=0,
                               n_classes=2,
                               n_clusters_per_class=2,
                               weights=None,
                               flip_y=0.01,
                               class_sep=1.0,
                               hypercube=True,
                               shift=0.0,
                               scale=1.0,
                               shuffle=True,
                               random_state=None)

    y[np.where(y == 0)[0]] = -1.

    estimator = SVC(C=10,
                    kernel='rbf',
                    gamma=0.4,
                    probability=True)
    pu_estimator = AdaPULearning(estimator, hold_out_ratio=0.2)

    pu_estimator.fit(X, y)

    print pu_estimator
    print
    print "Comparison of estimator and AdaPULearning(estimator):"
    print "Number of bad sales prospects: ", len(np.where((pu_estimator.predict(X) == estimator.predict(X)) == False)[0])
    print "Number of good sales prospects: ", len(np.where((pu_estimator.predict(X) == estimator.predict(X)) == True)[0])
