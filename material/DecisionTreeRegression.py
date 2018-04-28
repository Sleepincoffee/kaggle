import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder


def load_data(path):
    """
    加载excel文档并进行数据处理
    :param path:
    :return:
    """
    # 读取Excel文件
    df = pd.read_excel(path)

    df = df[['C', 'Si', 'Mn', 'Ni', 'Cr', 'Mo', 'Al', '等温温度T2', '回火温度T3', '抗拉强度']]
    print('Origin shape:', np.shape(df))
    print(df.shape[0] - df.count())
    # 重命名列名
    df = df.rename(columns={'等温温度T2': 'T2', '回火温度T3': 'T3', '抗拉强度': 'Y'})

    # 把所有列转为float 错误的置为N
    df = df.loc[:, :].apply(pd.to_numeric, errors='coerce')

    # 删除强度为空的行
    df = df[df.Y.notnull()]
    print('After delete NULL Y:', np.shape(df))
    # df.info()

    # 将列转为float errors={‘ignore’, ‘raise’, ‘coerce’} 返回数值 异常 置Nan
    # df.loc[:, 'C':'Al'] = df.loc[:, 'C':'Al'].apply(pd.to_numeric, errors='coerce')

    # 成分元素空值用0填充
    df.loc[:, 'C':'Al'] = df.loc[:, 'C':'Al'].fillna(value=0)
    """df.fillna({'C':0,'Si':0}) """

    # T3 填充室温 25
    df.loc[(df.T3.isnull()), 'T3'] = 25

    # T2 转为Float 错误的先删除
    # df.T2 = pd.to_numeric(df.T2, errors='coerce')
    df = df[df.T2.notnull()]
    # df.loc[:, 'T2'] = df.loc[:, 'T2'].fillna(value=25)

    return df


def preprocess(df, shuffle=True, categories=4, onehot=False):
    """
    数据预处理 默认打乱 4分类 不使用onehot
    :param df:
    :param shuffle:
    :param categories:
    :param onehot:
    :return:
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    X = df.loc[:, 'C':'T3'].as_matrix()
    y = df[['Y']].as_matrix()
    # y = deal_labels(y, categories=categories, onehot=onehot)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=shuffle, random_state=5)

    # 数据缩放
    # scaler = StandardScaler()
    # scaler = scaler.fit(X_train)
    # X_train = scaler.transform(X_train)
    # X_test = scaler.transform(X_test)

    # print([np.shape(x) for x in [X_train, X_test, y_train, y_test]])

    return X_train, X_test, y_train, y_test


def deal_labels(y, categories:'需要分成几个类别'=4, onehot:'是否使用onehot表示类别'=False):
    """
    将类别进行离散表示
    """
    # assert '<' not in str(y.dtype)
    min_ = np.min(y)
    max_ = np.max(y)
    # 设置分类边界
    bounds = np.linspace(min_-1, max_, categories+1)
    print('类别统计:', np.histogram(y, bounds)[0])
    # 画图
    # from matplotlib import pyplot as plt
    # plt.hist(y, bounds)
    # plt.title('Split Data with 4 categories')
    # plt.xlabel('Tensile Strength')
    # plt.ylabel('Count')
    # plt.show()
    # 转换类别编号
    y = [(bounds >= i).nonzero()[0][0] for i in y]
    # 编号下标从0开始
    y = y-np.array([1])
    y = y.ravel()

    # 是否使用onehot表示类别
    if onehot:
        y = np.array(y).reshape(-1,1)
        enc = OneHotEncoder()
        y = enc.fit_transform(y).toarray()
    return y


def compute_pearson(x, y):
    """
    计算pearson系数
    :param x:
    :param y:
    :return:
    """
    pearson = []
    for i in range(x.shape[1]):
        x_ = np.hstack(x[:, i])
        y_ = np.hstack(y)
        pearson.append(np.corrcoef(x_, y_)[1, 0])
    return pearson
    pass


def drawpic(df):
    from matplotlib import pyplot as plt
    plt.scatter(df.C, df.Y)
    plt.title('Carbon and tensile strength relationship scatter plot')
    plt.xlabel('Carbon content (wt.%)')
    plt.ylabel('Tensile Strength (MPa)')
    plt.show()


def evaluate_classifier(y, y_pred):
    """
    评估
    :param y:
    :param y_predt:
    :return:
    """
    # 计算F1 Recall support
    from sklearn.metrics import precision_recall_fscore_support as score
    precision, recall, fscore, support = score(y_test, y_pred)
    table = pd.DataFrame({'precision': precision, 'recall': recall, 'fscore': fscore, 'support': support})
    print(table)
    return table


def ecaluate_regression(y, y_pred):
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    y = y.ravel()
    y_pred = y_pred.ravel()
    print(y[:10])
    print(y_pred[:10])
    print(f'MAE:{mean_absolute_error(y, y_pred)}')
    print(f'MSE:{mean_squared_error(y, y_pred)}')
    print(f'RMSE:{np.sqrt(mean_squared_error(y, y_pred))}')
    pass


if __name__ == "__main__":
    # path = r'C:\Users\chenshuai\Documents\材料学院\贝氏体钢数据统计-总20180421_pd.xlsx'
    path = r'C:\Users\chenshuai\Documents\材料学院\贝氏体钢数据统计-chenshuai_pd.xlsx'
    data = load_data(path)
    # drawpic(data)
    data.info()

    train_accs = []
    test_accs = []
    es = []
    # for i in range(10):
    # 切分数据集
    X_train, X_test, y_train, y_test = preprocess(data, shuffle=False)

    for i in range(1):
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.model_selection import cross_val_score
        dtr = DecisionTreeRegressor(random_state=0)
        dtr.fit(X_train, y_train)
        y_pred = dtr.predict(X_test)
        train_acc = dtr.score(X_train, y_train)
        test_acc = dtr.score(X_test, y_test)
        train_accs.append(train_acc)
        test_accs.append(test_acc)
        print(f'Train Score: {train_acc:.2}  Test Score:{test_acc:.2}')
        # print(dtr.feature_importances_)
        es.append(dtr.feature_importances_)
        ecaluate_regression(y_test, y_pred)

    print(f'Train Score mean:{np.mean(train_accs):.2} Test Score mean:{np.mean(test_accs):.2}')
    print(f'Feature_importances mean:')
    df_importance = pd.DataFrame({'Gini':np.mean(es, axis=0)}, index=data.columns[:-1])
    df_importance = df_importance.sort_values(by='Gini', ascending=False)
    print(df_importance)

