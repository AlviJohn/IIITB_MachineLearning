# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 14:19:23 2018

@author: ajohn021
"""

import pandas as pd
import numpy as np
import seaborn as sns
import sys
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import scale
#import plotly

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.decomposition import IncrementalPCA


####Flag to determine if we want to use PCA in modeling or not
PCA_Flag=True



telecom_churn = pd.read_csv('telecom_churn_data.csv')
telecom_churn.info()
telecom_churn.shape
telecom_churn.head()
telecom_churn.describe()

###Finding high value accounts
#telecom_churn.drop(['totalrech_avg_goodphase'], axis = 1, inplace = True)
telecom_churn['totalrech_avg_goodphase']=(telecom_churn['total_rech_amt_6']+telecom_churn['total_rech_amt_7'])/2
telecom_churn = telecom_churn[telecom_churn['totalrech_avg_goodphase'] >  telecom_churn.totalrech_avg_goodphase.quantile(0.7)]



###Adding the churn status
telecom_churn['churn_status']= ((telecom_churn.total_ic_mou_9 <=0) & (telecom_churn.total_og_mou_9 <=0)
                                & (telecom_churn.vol_2g_mb_9 <=0) & (telecom_churn.vol_3g_mb_9 <=0)).astype('int')

###91% are non-converters
telecom_churn['churn_status'].value_counts()/telecom_churn['churn_status'].shape[0]

#####removing all month 9 values,date columns and circleId
telecom_churn_sub=telecom_churn[telecom_churn.columns.drop(list(telecom_churn.filter(regex='_9')))]
telecom_churn_sub=telecom_churn_sub[telecom_churn_sub.columns.drop(list(telecom_churn_sub.filter(regex='date')))]
telecom_churn_sub.drop(['circle_id'],axis=1,inplace=True)
telecom_churn_sub.shape


#######Removing rows having more than 50% of NA values. 0.7% values removed
telecom_churn_sub= telecom_churn_sub.loc[telecom_churn_sub.isnull().mean(axis=1) < 0.5,:]
telecom_churn_sub.shape

####### Removing columns having more than 60% of NA values.27 columns removed
telecom_churn_sub= telecom_churn_sub.loc[:,telecom_churn_sub.isnull().mean(axis=0) < 0.6]
telecom_churn_sub.shape


##Replacing NA's with median values for all the columns
telecom_churn_sub=telecom_churn_sub.apply(lambda x: x.fillna(x.median()),axis=0)



# splitting into X and y
X = telecom_churn_sub.drop("churn_status", axis = 1)
Y = telecom_churn_sub.churn_status.astype(int)
Y.value_counts()


###Scaling X values
X_scaled=scale(X)


####Splitting 70-30
X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size = 0.3, random_state = 100)



##PCA capturing ~  75% of variance(25 components) ##make sure flag is set in the beginning
pca = PCA(svd_solver='randomized', random_state=100)
pca.fit(X_train)
pca.explained_variance_ratio_
pd.DataFrame(pca.explained_variance_ratio_).to_csv('variance_explained.csv')
#fig = plt.figure(figsize = (40,8))
#plt.plot(np.cumsum(pca.explained_variance_ratio_))
#plt.xlabel('number of components')
#plt.ylabel('cumulative explained variance')
#plt.show()
pca_final = IncrementalPCA(n_components=25)

if PCA_Flag==True:
    X_train=pca_final.fit_transform(X_train)
    X_test=pca_final.fit_transform(X_test)

X_train.shape
X_test.shape  


####Recall seems to be the right metric since we are interested in identifying more churners correctly
##Recall <- Number of churners identified/Total number of churners
#####Random Forest/SVM/XG-Boost algorithms should give the best results for prediction.


#################################################################################

#####################################SVM##########################################

#################################################################################


model = SVC(C = 10000, kernel='rbf')
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(confusion_matrix(y_true=y_test, y_pred=y_pred))
####High value of C indicated high non-linearity. 

# accuracy,precision and recall. Ideally we should be looking at recall/True Positive rate 
print("accuracy", metrics.accuracy_score(y_test, y_pred))
print("precision", metrics.precision_score(y_test, y_pred))
print("recall", metrics.recall_score(y_test, y_pred))

#######Trying a grid search with K fold Validation
# creating a KFold object with 5 splits 
folds = KFold(n_splits = 5, shuffle = True, random_state = 100)
# specify range of hyperparameters
# Set the parameters by cross-validation
hyper_params = [ {'gamma': [1e-2, 1e-3, 1e-4],
                     'C': [100, 1000,1000]}]
# specify model
model = SVC(kernel="rbf")

# set up GridSearchCV()
model_cv = GridSearchCV(estimator = model, 
                        param_grid = hyper_params, 
                        scoring= 'recall', 
                        cv = folds, 
                        verbose = 1,
                        return_train_score=True)      

# fit the model
model_cv.fit(X_train, y_train)                  
# cv results
cv_results = pd.DataFrame(model_cv.cv_results_)
cv_results

# printing the optimal accuracy score and hyperparameters
best_score = model_cv.best_score_
best_hyperparams = model_cv.best_params_
print("The best test score is {0} corresponding to hyperparameters {1}".format(best_score, best_hyperparams))
#####Building Final Model#####
# specify optimal hyperparameters
best_params = {"C": , "gamma":, "kernel":"rbf"}
# model
model = SVC(C=, gamma=, kernel="rbf")
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# metrics
print(metrics.confusion_matrix(y_test, y_pred), "\n")
print("accuracy", metrics.accuracy_score(y_test, y_pred))
print("precision", metrics.precision_score(y_test, y_pred))
print("sensitivity/recall", metrics.recall_score(y_test, y_pred))

###################################End of SVM#######################################



#################################################################################

#####################################XG-BOOST##########################################

#################################################################################










