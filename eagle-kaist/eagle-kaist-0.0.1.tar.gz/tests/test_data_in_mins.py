from eagle_heart.data_utils import generate_features, summarize_data_in_day
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
# %matplotlib inline
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



# input_file = "./test_database/hpg_mins/2021-06-01_min_base.csv"
input_file = "./test_database/hpg_mins/2021-06-04_min.csv"
output_file = "./test_database/hpg_mins/2021-06-04_min_features.csv"

df = pd.read_csv(input_file)
# generate_features(df)
output_df = generate_features(df)
output_df.to_csv(output_file)

# input_file = "./test_database/2021-06-08/stock_hpg/hpg_price_hist_1min.csv"
# output_file = "./test_database/test_data_in_mins/hpg_price_hist_1min_output.csv"

# def generate_feature(input_file, output_file):
#     data = pd.read_csv(input_file)
#     data['Money'] = data['Volumn'] * data['Close'] 
#     daily_money = data['Money'].sum()
    


def plot_data(input_file):
    parsing_date = False
    if parsing_date:
        data = pd.read_csv(input_file, parse_dates=['Date'], index_col=['Date'])
    else:
        data = pd.read_csv(input_file)
    data['Money'] = data['Volumn'] * data['Close']
    print(data)
    date_form = DateFormatter("%Y-%m-%d %H:%M")
    # Use white grid plot background from seaborn
    sns.set(font_scale=1.5, style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(24, 12))
    fig, ax1 = plt.subplots()
    color1 = 'tab:red'
    ax1.set_ylabel('Money', color=color1)
    # ax1.bar(data.index.values, data['Money'], color=color1)
    # ax1.plot(data['Money'], color=color1)
    # ax1.xaxis.set_major_formatter(date_form)
    # sns.lineplot(data=data['Money'], color=color1, ax=ax1)
    sns.barplot(data=data['Money'], color=color1, ax=ax1)
    ax1.tick_params(axis='y', labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = 'tab:blue'
    ax2.set_ylabel('Close', color=color2)
    # ax2.bar(data.index.values, data['Close'], color=color2)
    # ax2.plot(data['Close'], color=color2)
    # ax2.xaxis.set_major_formatter(date_form)
    # sns.lineplot(data=data['Close'], color=color2, ax=ax2)
    sns.barplot(data=data['Close'], color=color2, ax=ax2)
    ax2.tick_params(axis='y', labelcolor=color2)

    # plt.plot(data['Date'], data['Close'])
    # fig.tight_layout() 
    # plt.show()
    # plt.waitforbuttonpress()

    # sns.lineplot(data=data)
    # plt.show()
    plt.waitforbuttonpress()

