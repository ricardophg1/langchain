# Business Analytics Pro

A comprehensive business analytics platform with AI-powered insights, multi-tenant architecture, and seamless ERP/CRM integrations.

## Project Overview

Business Analytics Pro is a Python-based Streamlit application that provides advanced business analytics capabilities:

- 📊 **Multi-dimensional Analytics**: Financial, Commercial, and Operational dashboards
- 🤖 **AI-powered Insights**: Predictive analysis and recommendations
- 🔗 **Integration Hub**: Connect with ERP, CRM, and other business systems
- 👥 **Multi-tenancy**: Support for multiple organizations with isolated data
- 🔒 **Enterprise Security**: Role-based access control and data protection

## Technical Requirements

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Required Python Packages

```
streamlit==1.29.0
openai>=1.10.0
python-dotenv==1.0.0
plotly==5.18.0
pandas==2.1.4
statsmodels==0.14.1
```

## Running the Application

1. **Install Python Dependencies**

   ```bash
   pip install -r requirements/prod.txt
   ```

2. **Set Up Environment Variables**

   Create a `.env` file in the root directory with the following:

   ```
   OPENAI_API_KEY=your_openai_api_key
   APP_ENVIRONMENT=development
   ```

3. **Run the Streamlit Application**

   ```bash
   cd business-analytics-pro
   streamlit run langchain_project/main.py
   ```

   For debug mode:

   ```bash
   cd business-analytics-pro
   streamlit run langchain_project/main.py --debug
   ```

## Project Structure

```
├─ business-analytics-pro/          # Main application directory
│  ├─ config/                       # Configuration files
│  ├─ langchain_project/            # Core application code
│  │  ├─ analytics/                 # Analytics modules
│  │  ├─ components/                # Reusable UI components
│  │  ├─ data_connector/            # Data source connectors
│  │  ├─ erp_crm_integration/       # ERP/CRM integration modules
│  │  ├─ models/                    # AI models
│  │  ├─ multi_tenancy/             # Multi-tenant functionality
│  │  ├─ pages/                     # Application pages
│  │  ├─ security_system/           # Security and authentication
│  │  ├─ utils/                     # Utility functions
│  │  └─ main.py                    # Main application entry point
│  └─ requirements/                 # Package requirements
├─ docs/                            # Documentation
└─ tests/                           # Test suite
```

## Features

### Dashboard Analytics

- **KPI Monitoring**: Track key performance indicators in real-time
- **Interactive Visualizations**: Drag-and-drop chart creation
- **Custom Reports**: Generate and export custom reports

### Financial Analytics

- **Revenue Analysis**: Track revenue streams and identify trends
- **Expense Management**: Monitor and categorize expenses
- **Profitability Analysis**: Analyze profit margins by product/service
- **Budget Tracking**: Compare actual vs. budgeted figures

### Commercial Analytics

- **Sales Performance**: Track sales by region, product, and rep
- **Customer Analysis**: Customer segmentation and lifetime value
- **Pipeline Management**: Visualize and forecast sales pipeline
- **Market Analysis**: Identify market trends and opportunities

### Operational Analytics

- **Process Efficiency**: Identify bottlenecks and inefficiencies
- **Quality Metrics**: Monitor quality indicators and defects
- **Resource Utilization**: Track resource allocation and utilization
- **Supply Chain Visibility**: Monitor inventory and supplier performance

### AI-Powered Insights

- **Predictive Analytics**: Forecast trends and outcomes
- **Anomaly Detection**: Identify unusual patterns or outliers
- **Recommendation Engine**: Get actionable recommendations
- **Natural Language Interface**: Chat with your data using AI

## Development

### Setting Up Development Environment

1. **Install Development Dependencies**

   ```bash
   pip install -r requirements/dev.txt
   ```

2. **Run Tests**

   ```bash
   python -m pytest tests/
   ```

## Troubleshooting

### Common Issues

1. **Streamlit Not Starting**:

   - Check if streamlit is installed: `pip show streamlit`
   - Verify that port 8501 is not in use

2. **OpenAI API Key Issues**:

   - Ensure your API key is valid and has sufficient credits
   - Check if the .env file is correctly formatted

3. **Data Connection Issues**:
   - Verify network connectivity to data sources
   - Check authentication credentials for integrated systems

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
