# Smart Product Recommendation System

An intelligent e-commerce recommendation system using collaborative filtering and item similarity.

## Overview
This project implements a smart recommendation system that suggests similar products to users based on their past interactions. It uses item-based collaborative filtering with cosine similarity, implemented in Python and presented through an interactive Streamlit dashboard.

## Features
- Item-based collaborative filtering
- Real-time product recommendations
- Interactive web dashboard
- Cosine similarity calculations
- Top-N similar products suggestions

## Project Structure
```
smart-info-project/
├── data/
│   └── Enhanced_Ecommerce_Dataset.csv
├── src/
│   ├── recommender.py      # Core recommendation logic
│   └── dashboard.py        # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   streamlit run src/dashboard.py
   ```

## Technologies Used
- Python 3.8+
- pandas
- scikit-learn
- Streamlit
- numpy
