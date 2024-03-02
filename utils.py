from Step2_Queue_Model import ShiftQueueModel
from Step3_Genetic_Algorithm import Genetic
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

def plot_save(df1, is_save):
    '''
    plot dist
    :param df1:
    :param is_save:
    :return:
    '''
    df1 = df1[df1['Response Time'] != 0]

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(10, 3))

    sns.lineplot(x=range(len(df1[df1['Level'] == 'Immediate'])), y='Response Time',
                 data=df1[df1['Level'] == 'Immediate'], marker='o', linestyle='-', color='b', ax=axes[0],
                 label='Immediate')
    axes[0].set_ylabel('Response Time (hrs)')
    axes[0].set_ylim([0, 1])
    axes[0].legend()
    axes[0].get_xaxis().set_visible(False)

    sns.lineplot(x=range(len(df1[df1['Level'] == 'Prompt'])), y='Response Time',
                 data=df1[df1['Level'] == 'Prompt'], marker='s', linestyle='-', color="#ffc34e", ax=axes[1],
                 label='Prompt')
    axes[1].legend()
    axes[1].set_ylim([0, 3])
    axes[1].get_xaxis().set_visible(False)

    sns.lineplot(x=range(len(df1[df1['Level'] == 'Standard'])), y='Response Time',
                 data=df1[df1['Level'] == 'Standard'], marker='o', linestyle='-', color="#038355", ax=axes[2],
                 label='Standard')
    axes[2].legend()
    axes[2].set_ylim([0, 6])
    axes[2].get_xaxis().set_visible(False)

    plt.tight_layout()
    if is_save:
        plt.savefig(r'.\solve shift 2\14 5 6.png', dpi=300, bbox_inches='tight')

    plt.show()

def plot_3d(data, optimal, is_save):
    '''
    plot 3d solutions
    :param data:
    :param optimal:
    :param is_save:
    :return:
    '''
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    for point in data:
        ax.scatter(point[0], point[1], point[2], c='b', marker='o')

    ax.scatter(optimal[0], optimal[1], optimal[2], c='r', marker='s', s=10, label=f'{optimal}')
    ax.scatter(5, 3, 7, c='b', marker='o', label='random')

    ax.set_xlabel('station1')
    ax.set_ylabel('station2')
    ax.set_zlabel('station3')

    ax.legend()

    # plt.title('initial strategy')

    if is_save:
        plt.savefig(r'.\solve shift 2\random.png', dpi=300, bbox_inches='tight')

    plt.show()