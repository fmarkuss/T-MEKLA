from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
import base64
import sqlite3
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
DATABASE = 'data.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    value INTEGER,
                    category TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)
        save_to_db(df)
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/visualize')
def visualize():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    
    img = BytesIO()
    plt.figure(figsize=(6,4))
    plt.hist(df['value'], bins=10, color='blue', alpha=0.7)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Values')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return render_template('visualize.html', plot_url=plot_url)

@app.route('/summary')
def summary():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    desc = df.describe().to_html()
    return render_template('summary.html', table=desc)

@app.route('/scatter')
def scatter_plot():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    
    img = BytesIO()
    plt.figure(figsize=(6,4))
    sns.scatterplot(x=df.index, y=df['value'], hue=df['category'])
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Scatter Plot of Values')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return render_template('scatter.html', plot_url=plot_url)

@app.route('/bar_chart')
def bar_chart():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT category, AVG(value) as avg_value FROM data GROUP BY category", conn)
    conn.close()
    fig = px.bar(df, x='category', y='avg_value', title='Average Value per Category')
    chart_html = fig.to_html(full_html=False)
    return render_template('bar_chart.html', chart_html=chart_html)

@app.route('/line_chart')
def line_chart():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    fig = px.line(df, x=df.index, y='value', title='Line Chart of Values')
    chart_html = fig.to_html(full_html=False)
    return render_template('line_chart.html', chart_html=chart_html)

@app.route('/box_plot')
def box_plot():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    fig = px.box(df, x='category', y='value', title='Box Plot of Values by Category')
    chart_html = fig.to_html(full_html=False)
    return render_template('box_plot.html', chart_html=chart_html)

@app.route('/pie_chart')
def pie_chart():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT category, COUNT(*) as count FROM data GROUP BY category", conn)
    conn.close()
    fig = px.pie(df, names='category', values='count', title='Distribution of Categories')
    chart_html = fig.to_html(full_html=False)
    return render_template('pie_chart.html', chart_html=chart_html)

@app.route('/heatmap')
def heatmap():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()
    img = BytesIO()
    plt.figure(figsize=(6,4))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
    plt.title('Heatmap of Correlations')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('heatmap.html', plot_url=plot_url)

def save_to_db(df):
    conn = sqlite3.connect(DATABASE)
    df.to_sql('data', conn, if_exists='replace', index=False)
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)


