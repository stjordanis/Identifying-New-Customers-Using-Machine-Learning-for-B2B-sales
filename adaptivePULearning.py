import numpy as np


class AdaPULearning(object):
    """
        PU-learning Using an Adapted Classifier
        
        As proposed by:
        PATRIK NORLIN
        VIKTOR PAULSRUD
        STOCKHOLM , SWEDEN 2017

        Identifying New Customers
        Using Machine Learning
        A case study on B2B-sales in the Swedish IT-
        consulting sector

        Link: https://pdfs.semanticscholar.org/9813/21d9f06a51110d6585bce4dcc14f624acbc0.pdf

    """

    def __init__(self, estimator, hold_out_ratio=0.1, precomputed_kernel=False):
        """
        estimator -- An estimator of p(s=1|x) that must implement:
                     * predict_proba(X): Takes X, which can be a list of feature vectors or a precomputed
                                         kernel matrix and outputs p(s=1|x) for each example in X
                     * fit(X,y): Takes X, which can be a list of feature vectors or a precomputed
                                 kernel matrix and takes y, which are the labels associated to the
                                 examples in X
        hold_out_ratio -- The ratio of training examples that must be held out of the training set of examples
                          to estimate p(s=1|y=1) after training the estimator
        precomputed_kernel -- Specifies if the X matrix for predict_proba and fit is a precomputed kernel matrix
        """
        self.estimator = estimator
        self.c = 1.0
        self.hold_out_ratio = hold_out_ratio

        if precomputed_kernel:
            self.fit = self.__fit_precomputed_kernel
        else:
            self.fit = self.__fit_no_precomputed_kernel

        self.estimator_fitted = False

    def __str__(self):
        return 'Estimator:' + str(self.estimator) + '\n' + 'p(s=1|y=1,x) ~= ' + str(self.c) + '\n' + \
               'Fitted: ' + str(self.estimator_fitted)

    def __fit_precomputed_kernel(self, X, y):
        """
        Fits an estimator of p(s=1|x) and estimates the value of p(s=1|y=1) using a subset of the training examples
        X -- Precomputed kernel matrix
        y -- Labels associated to each example in X (Positive label: 1.0, Negative label: -1.0)
        """
        positives = np.where(y == 1.)[0]
        hold_out_size = np.ceil(len(positives) * self.hold_out_ratio)

        if len(positives) <= hold_out_size:
            raise ('Not enough positive examples to estimate p(s=1|y=1,x). Need at least ' + str(
                hold_out_size + 1) + '.')

        np.random.shuffle(positives)
        hold_out = positives[:hold_out_size]

        # Hold out test kernel matrix
        X_test_hold_out = X[hold_out]
        keep = list(set(np.arange(len(y))) - set(hold_out))
        X_test_hold_out = X_test_hold_out[:, keep]

        # New training kernel matrix
        X = X[:, keep]
        X = X[keep]

        y = np.delete(y, hold_out)

        self.estimator.fit(X, y)

        hold_out_predictions = self.estimator.predict_proba(X_test_hold_out)

        try:
            hold_out_predictions = hold_out_predictions[:, 1]
        except:
            pass

        c = np.mean(hold_out_predictions)
        self.c = c

        self.estimator_fitted = True

    def __fit_no_precomputed_kernel(self, X, y):
        """
        Fits an estimator of p(s=1|x) and estimates the value of p(s=1|y=1,x)
        X -- List of feature vectors
        y -- Labels associated to each feature vector in X (Positive label: 1.0, Negative label: -1.0)
        """
        positives = np.where(y == 1.)[0]
        hold_out_size = np.ceil(len(positives) * self.hold_out_ratio)

        if len(positives) <= hold_out_size:
            raise ('Not enough positive examples to estimate p(s=1|y=1,x). Need at least ' + str(
                hold_out_size + 1) + '.')

        np.random.shuffle(positives)
        hold_out = positives[:hold_out_size]
        X_hold_out = X[hold_out]
        X = np.delete(X, hold_out, 0)
        y = np.delete(y, hold_out)

        self.estimator.fit(X, y)

        hold_out_predictions = self.estimator.predict_proba(X_hold_out)

        try:
            hold_out_predictions = hold_out_predictions[:, 1]
        except:
            pass

        c = np.mean(hold_out_predictions)
        self.c = c

        self.estimator_fitted = True

    def predict_proba(self, X):
        """
        Predicts p(y=1|x) using the estimator and the value of p(s=1|y=1) estimated in fit(...)
        X -- List of feature vectors or a precomputed kernel matrix
        """
        if not self.estimator_fitted:
            raise Exception('The estimator must be fitted before calling predict_proba(...).')

        probabilistic_predictions = self.estimator.predict_proba(X)

        try:
            probabilistic_predictions = probabilistic_predictions[:, 1]
        except:
            pass

        return probabilistic_predictions / self.c

    def predict(self, X, treshold=0.5):
        """
        Assign labels to feature vectors based on the estimator's predictions
        X -- List of feature vectors or a precomputed kernel matrix
        treshold -- The decision treshold between the positive and the negative class
        """
        if not self.estimator_fitted:
            raise Exception('The estimator must be fitted before calling predict(...).')

        return np.array([1. if p > treshold else -1. for p in self.predict_proba(X)])