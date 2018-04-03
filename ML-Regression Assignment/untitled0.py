import pandas as pd
import numpy as np
import seaborn as sns
import sys
import os
import matplotlib.pyplot as plt
import plotly

# Data Import
car_price = pd.read_csv('CarPrice_Assignment.csv')
car_price.info()
car_price.shape
car_price.head()


car_price['companyname']=car_price['CarName'].str.split().str.get(0)
car_price.companyname

car_price=car_price.drop(['CarName'],axis=1)


## Data Preparation 

###Creating Dummies
fueltype = pd.get_dummies(car_price['fueltype'],drop_first=True,prefix='fueltype')
aspiration = pd.get_dummies(car_price['aspiration'],drop_first=True,prefix='aspiration')
doornumber = pd.get_dummies(car_price['doornumber'],drop_first=True,prefix='doornumber')
enginelocation = pd.get_dummies(car_price['enginelocation'],drop_first=True,prefix='enginelocation')
symboling= pd.get_dummies(car_price['symboling'],drop_first=True ,prefix='symboling')
companyname = pd.get_dummies(car_price['companyname'],drop_first=True,prefix='companyname')
carbody = pd.get_dummies(car_price['carbody'],drop_first=True,prefix='carbody')
drivewheel = pd.get_dummies(car_price['drivewheel'],drop_first=True,prefix='drivewheel')
enginetype = pd.get_dummies(car_price['enginetype'],drop_first=True,prefix='enginetype')
cylindernumber = pd.get_dummies(car_price['cylindernumber'],drop_first=True,prefix='cylindernumber')
fuelsystem = pd.get_dummies(car_price['fuelsystem'],drop_first=True,prefix='fuelsystem')
 
### Adding all the dummy variables to car_price file
car_price = pd.concat([car_price,fueltype,aspiration,doornumber,enginelocation,symboling,companyname,carbody,drivewheel,enginetype,cylindernumber,fuelsystem],axis=1)
print(car_price.shape)
car_price = car_price.drop(['fueltype','aspiration','doornumber','enginelocation','symboling','companyname','carbody','drivewheel','enginetype','cylindernumber','fuelsystem'],axis=1)
print(car_price.shape)


## selecting the numerical variables 
#%matplotlib inline
#
#car_num_vars=['wheelbase','carlength','carwidth','carheight','curbweight',
#              'enginesize','boreratio', 'stroke','compressionratio','horsepower','peakrpm','citympg','highwaympg','price']
#plt.figure(figsize = (25,15))
#sns.pairplot(car_price, x_vars=car_num_vars[0:-1], y_vars='price',size=3, aspect=.7, kind='scatter')

## Let's see the correlation matrix 
#plt.figure(figsize = (16,10))     # Size of the figure
#sns.heatmap(car_price[car_num_vars].corr(),annot = True)
#We can clearly see that price is highly correlated with curbweight,engine size and horsepower


# Importing RFE and LinearRegression
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

#defining a normalisation function 
def normalize (x): 
    return ( (x-np.mean(x))/ (max(x) - min(x)))
# applying normalize ( ) to all columns 
car_price_norm = car_price.apply(normalize) 
y = car_price_norm['price']
print(y.shape)
X = car_price_norm
X=X.drop(['car_ID','price'],axis=1)
print(X.shape)

## Splitting test and train
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8 ,test_size = 0.2, random_state=100)


# VIF function
def vif_cal(input_data, dependent_col):
    vif_df = pd.DataFrame( columns = ['Var', 'Vif'])
    x_vars=input_data.drop([dependent_col], axis=1)
    xvar_names=x_vars.columns
    for i in range(0,xvar_names.shape[0]):
        y=x_vars[xvar_names[i]] 
        x=x_vars[xvar_names.drop(xvar_names[i])]
        rsq=sm.OLS(y,x).fit().rsquared  
        vif=round(1/(1-rsq),2)
        vif_df.loc[i] = [xvar_names[i], vif]
    return vif_df.sort_values(by = 'Vif', axis=0, ascending=False, inplace=False)


###running a loop to get the best 30 variables before manually tweaking the models . In each pass,
##makaing sure that all variables having p value greater than .2 and vif greater than 20 is removed 
##This will ensure that we have a decent model to start with    
X_train_loop=X_train
for num in range(70,30,-1):
    lm = LinearRegression()
    rfe = RFE(lm, num)             
    rfe = rfe.fit(X_train_loop, y_train)
    print(X_train_loop.columns)
    print(rfe.support_)           
    col_list = X_train_loop.columns[rfe.support_]
     # Creating X_test dataframe with RFE selected variables
    X_train_rfe = X_train_loop[col_list]
    
    # Adding a constant variable 
    import statsmodels.api as sm  
    X_train_rfe['const']=1
    lm = sm.OLS(y_train,X_train_rfe).fit()   # Running the linear model
    #Let's see the summary of our linear model
    vif_values=vif_cal(input_data=car_price_norm[col_list.tolist() + ['price']], dependent_col="price")
    remove= X_train_rfe.columns[lm.pvalues>.2].tolist() + vif_values[vif_values.Vif > 20].Var.tolist()
    if 'const' in remove:
        remove.remove('const')
    if len(remove) > 0:
        X_train_loop.drop(remove,axis=1,inplace=True)
    else:
         pass

lm.summary()
vif_values



##Checking correlation once again
plt.figure(figsize = (16,10))     
sns.heatmap(X_train_loop.corr(),annot = True)

######VIF is good for all removing variables having p value greater than .1. 
X_train_loop.drop(['companyname_mitsubishi'],axis=1,inplace=True)
X_train_loop['const']=1
lm = sm.OLS(y_train,X_train_loop).fit()
print(lm.summary())
##Now p values are less than .09

###Checking Vif again. Every value looks good
var_list=X_train_loop.columns.tolist() + ['price']
var_list.remove('const')
vif_values=vif_cal(input_data=car_price_norm[var_list], dependent_col="price")
print(vif_values)


# Making predictions on test
var_list.remove('price')
X_test_loop = X_test[var_list]
X_test_loop['const']=1
y_pred = lm.predict(X_test_loop)

# Actual and Predicted
import matplotlib.pyplot as plt
c = [i for i in range(1,42,1)] # generating index 
fig = plt.figure() 
plt.plot(c,y_test, color="blue", linewidth=2.5, linestyle="-") #Plotting Actual
plt.plot(c,y_pred, color="red",  linewidth=2.5, linestyle="-") #Plotting predicted
fig.suptitle('Actual and Predicted', fontsize=20)              # Plot heading 
plt.xlabel('Index', fontsize=18)                               # X-label
plt.ylabel('car_price', fontsize=16) 

# Plotting y_test and y_pred to understand the spread.
fig = plt.figure()
plt.scatter(y_test,y_pred)
fig.suptitle('y_test vs y_pred', fontsize=20)              # Plot heading 
plt.xlabel('y_test', fontsize=18)                          # X-label
plt.ylabel('y_pred', fontsize=16)    


# Plotting the error terms to understand the distribution.Errors are gaussian
fig = plt.figure()
sns.distplot((y_test-y_pred),bins=20)
fig.suptitle('Error Terms', fontsize=20)                  # Plot heading 
plt.xlabel('y_test-y_pred', fontsize=18)                  # X-label
plt.ylabel('Index', fontsize=16)      

###Checking RMSE. 14% error
import numpy as np
from sklearn import metrics
print('RMSE :', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

