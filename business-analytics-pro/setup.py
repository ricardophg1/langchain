from setuptools import setup, find_packages

setup(
    name="langchain_project",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.29.0",
        "openai>=1.10.0",
        "python-dotenv==1.0.0",
        "plotly==5.18.0",
        "pandas==2.1.4",
        "statsmodels==0.14.1",
        "PyJWT==2.8.0",
        "sqlalchemy==2.0.27",
        "scikit-learn==1.4.0"  # Adicionando scikit-learn para análise preditiva
    ],
)