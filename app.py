from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                df = pd.read_excel(filepath)
                
                x_column = request.form.get('x_select')
                y_columns = request.form.getlist('y_select')

                plt.figure(figsize=(10, 6))
                for y_column in y_columns:
                    plt.plot(df[x_column], df[y_column], label=y_column)

                plt.xlabel(x_column)
                plt.ylabel('Values')
                plt.title('Plot Title')
                plt.legend(title='Legend')
                plot_filename = 'figure.png'
                plt.savefig(f'static/{plot_filename}')
                plt.clf()

                return render_template('index.html', columns=df.columns, plot_filename=plot_filename, filename=file.filename, x_column=x_column, y_columns=y_columns, stats=None)

    return render_template('index.html', columns=[], plot_filename=None, filename=None, x_column=None, y_columns=[], stats=None)

@app.route('/columns', methods=['POST'])
def get_columns():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)
            columns = df.columns.tolist()
            return jsonify(columns=columns)
    return jsonify(columns=[])

@app.route('/statistics', methods=['POST'])
def statistics():
    x_column = request.form.get('x_column')
    y_columns = request.form.get('y_columns').strip('][').split(', ')
    selected_statistics = request.form.getlist('statistics_select')
    filename = request.form.get('filename')

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)

    stats = {}

    if not df.empty and x_column and y_columns:
        y_columns = [col.strip("'") for col in y_columns]
        if 'mean' in selected_statistics:
            stats['mean'] = df[y_columns].mean().to_dict()
        if 'median' in selected_statistics:
            stats['median'] = df[y_columns].median().to_dict()
        if 'mode' in selected_statistics:
            stats['mode'] = df[y_columns].mode().iloc[0].to_dict()
        if 'range' in selected_statistics:
            stats['range'] = (df[y_columns].max() - df[y_columns].min()).to_dict()
        if 'variance' in selected_statistics:
            stats['variance'] = df[y_columns].var().to_dict()
        if 'std_dev' in selected_statistics:
            stats['std_dev'] = df[y_columns].std().to_dict()
        if 'correlation' in selected_statistics:
            correlation = {}
            for y_column in y_columns:
                correlation[y_column] = df[[x_column, y_column]].corr().iloc[0, 1]
            stats['correlation'] = correlation

    return render_template('index.html', columns=df.columns, plot_filename='figure.png', filename=filename, x_column=x_column, y_columns=y_columns, stats=stats)

if __name__ == '__main__':
    app.run()