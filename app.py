import ast
import csv
import json

import numpy as np
import statsmodels.api as sm

from flask import Flask, render_template, redirect, jsonify
import networkx as nx

app = Flask(__name__)

def read_csv():
    data = []
    with open('static/csv_data/file.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)

    return data

# 从文件中读取边的数据
def read_edges_from_file(file_path):
    edges = []
    with open(file_path, 'r+', encoding='utf-8') as f:
        for line in f:
            lists = ast.literal_eval(line)
            edges.append(lists[0])
    return edges

# 将边的数据转换为ECharts所需的节点和边数据格式
def convert_to_echarts_data(edges):
    nodes = []
    links_source = []
    links_target = []
    for edge in edges:
        source, target = edge
        # 添加节点
        if source not in nodes:
            nodes.append(source)
        if target not in nodes:
            nodes.append(target)
        # 添加边
        links_source.append(source)
        links_target.append(target)

    nodes = set(nodes)
    nodes = list(nodes)
    return nodes, links_source, links_target

# def getgraphProperty(nodes, links_source, links_target):
#     # 创建一个空的无向图
#     G = nx.Graph()
#
#     # 添加节点
#     for node in nodes:
#         G.add_node(node)
#
#     # 添加边
#     for i in range(len(links_source)):
#         source = links_source[i]
#         target = links_target[i]
#         G.add_edge(source, target)
#
#     # 计算每个节点的度
#     degrees = G.degree()
#
#     # 使用合适的社区检测算法进行社区划分
#     # 这里使用Louvain算法作为示例，你可以根据需要选择其他算法
#     communities = nx.algorithms.community.label_propagation.label_propagation_communities(G)
#
#     return degrees, communities

# 获取节点所属的社区
def get_community(node, communities):
    for i, community in enumerate(communities):
        if node in community:
            return i
    return -1  # 如果无法找到节点的社区，返回-1或其他标识

def get_tag(p_value_list):
    starred_p_values = []
    for p_value in p_value_list:
        if float(p_value) < 0.001:
            starred_p_values.append('***')
        elif float(p_value) < 0.01:
            starred_p_values.append('**')
        elif float(p_value) < 0.05:
            starred_p_values.append('*')
        elif float(p_value) < 0.1:
            starred_p_values.append('.')
        else:
            starred_p_values.append('')

    return starred_p_values

def get_project_data(data):
    NewC = []
    DSN_features = []
    # project_features = []
    DSN_size = []
    DSN_density = []
    DSN_bridge = []
    DSN_avg_degree_centrality = []
    for i in range(0, len(data)):
        NewC.append(data[i]['NewC'])
        DSN_size.append(data[i]['DSN size'])
        DSN_density.append(data[i]['DSN density'])
        DSN_bridge.append(data[i]['DSN bridges'])
        DSN_avg_degree_centrality.append(data[i]['Avg_degree_centrality'])
        # sponsor.append(data[i]['sponsor'])
        # project_size.append(data[i]['project size'])
        # avg_experience.append(data[i]['Avg experience'])

    DSN_size = [float(x) for x in DSN_size]
    DSN_density = [float(x) for x in DSN_density]
    DSN_bridge = [float(x) for x in DSN_bridge]
    DSN_avg_degree_centrality = [float(x) for x in DSN_avg_degree_centrality]
    NewC = [float(x) for x in NewC]
    # sponsor = [float(x) for x in sponsor]
    # project_size = [float(x) for x in project_size]
    # avg_experience = [float(x) for x in avg_experience]

    for list_DSN in [DSN_size, DSN_density, DSN_bridge, DSN_avg_degree_centrality]:
        DSN_features.append(list_DSN)

    # for list_project in [project_size, avg_experience, sponsor]:
    #     project_features.append(list_project)

    return DSN_features, NewC

def get_regression_data(results):
    regression_data = []

    # 提取拟合结果
    params = results.params
    p_values = results.pvalues

    formatted_params = ["{:.3f}".format(param) for param in params]
    formatted_p_values = ["{:.3f}".format(p_value) for p_value in p_values]

    stared_p_values_project_size = get_tag(formatted_p_values)

    regression_data.append(formatted_params)
    regression_data.append(stared_p_values_project_size)

    r2 = results.rsquared
    adj_r2 = results.rsquared_adj
    f_statistic = results.fvalue

    formatted_r2 = "{:.3f}".format(r2)
    formatted_adj_r2 = "{:.3f}".format(adj_r2)
    foarmatted_f_statistic = "{:.3f}".format(f_statistic)

    regression_data.append(formatted_r2)
    regression_data.append(formatted_adj_r2)
    regression_data.append(foarmatted_f_statistic)

    return regression_data


def regression(DSN_features, NewC):
    regression_list = []

    # 准备数据
    x1 = np.array(DSN_features[0])
    x2 = np.array(DSN_features[1])
    x3 = np.array(DSN_features[2])
    x4 = np.array(DSN_features[3])
    y = np.array(NewC)
    X5 = np.column_stack((x1, x2, x3, x4))

    # 添加常数项
    x1 = sm.add_constant(x1)
    x2 = sm.add_constant(x2)
    x3 = sm.add_constant(x3)
    x4 = sm.add_constant(x4)
    X5 = sm.add_constant(X5)

    model_DSN_size = sm.OLS(y, x1)
    results_DSN_size = model_DSN_size.fit()
    print(results_DSN_size.summary())
    print(results_DSN_size.fvalue)

    model_DSN_density = sm.OLS(y, x2)
    results_DSN_density = model_DSN_density.fit()

    model_DSN_bridge = sm.OLS(y, x3)
    results_DSN_bridge = model_DSN_bridge.fit()

    model_DSN_degree_centrality = sm.OLS(y, x4)
    results_DSN_degree_centrality = model_DSN_degree_centrality.fit()

    model_DSN_composit = sm.OLS(y, X5)
    results_DSN_composit = model_DSN_composit.fit()
    print(results_DSN_composit.summary())

    DSN_size_regression_results = get_regression_data(results_DSN_size)
    DSN_density_regression_results = get_regression_data(results_DSN_density)
    DSN_bridge_regression_results = get_regression_data(results_DSN_bridge)
    DSN_degree_centrality_regression_results = get_regression_data(results_DSN_degree_centrality)
    DSN_composit_regression_results = get_regression_data(results_DSN_composit)


    regression_list.append(DSN_size_regression_results)
    regression_list.append(DSN_density_regression_results)
    regression_list.append(DSN_bridge_regression_results)
    regression_list.append(DSN_degree_centrality_regression_results)
    regression_list.append(DSN_composit_regression_results)

    return regression_list




@app.route('/')
def index():
    data = read_csv()

    DSN_features, NewC = get_project_data(data)

    regression_list = regression(DSN_features, NewC)

    print(regression_list)

    # values = [1, 2, 3, 3, 4, 5, 5, 5, 6, 6, 6, 6, 7, 8, 9]

    return render_template('index.html', data=data, regression_list=regression_list, DSN_features=DSN_features, NewC=NewC)

# @app.route('/details/<int:index>')
# def Nodes(index):


@app.route('/details/<int:index>')
def details(index):
    data = read_csv()
    details_data = data[index-1]

    print(details_data)

    # 从数据行中获取项目属性的值
    project_value = details_data['Project']

    # 读取文件中的边数据，并转换为ECharts所需的数据格式
    edges = read_edges_from_file('static/network_data/' + project_value + '_network_weightedge')
    nodes, links_source, links_target = convert_to_echarts_data(edges)
    # degrees, communities = getgraphProperty(nodes, links_source, links_target)


    # 将度和社区信息添加到节点数据中
    # Nodes = []
    # for node in nodes:
    #     degree = degrees[node]
    #     community = get_community(node, communities)
    #     node_data = {"name": node, "degree": degree, "community": community}
    #     Nodes.append(node_data)


    # 将 Nodes 转换为 JSON 格式
    # Nodes = json.dumps(Nodes)

    print(nodes, links_source, links_target)

    return render_template('detail.html', data=details_data, project_value=project_value, links_source=links_source, links_target=links_target, nodes=nodes)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
