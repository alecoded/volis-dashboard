# 🚀 Volis Executive Intelligence Dashboard

Modern C-Level analytics platform built with **Python, Reflex, DuckDB and dbt**, transforming raw e-commerce data into executive decision-making insights.

---

## ✨ Overview

This project was developed as part of a Data Analyst technical assessment focused on business thinking, analytics engineering, and executive storytelling.

Using the **Olist Brazilian E-commerce Dataset**, the objective was to create a modern dashboard that gives leadership teams immediate visibility into company performance.

---

## 🎯 Business Questions Solved

* Are we growing revenue consistently?
* Which states are creating logistics bottlenecks?
* How satisfied are customers?
* Which product categories need intervention?
* Where should we expand our seller network?
* How competitive is our freight structure?

---

## 🖥 Dashboard Preview

<img width="928" height="862" alt="image" src="https://github.com/user-attachments/assets/c4fa8542-bac8-4098-9263-6567d3fd79fd" />
<p><em> Header KPIs and CFO View — Revenue trends, average ticket and state performance.</em></p>





<img width="910" height="882" alt="image" src="https://github.com/user-attachments/assets/4852adf7-eaaf-4d55-98d0-3d46237e33bd" />
<p><em>COO View — Delivery SLA, logistics bottlenecks and operational efficiency.</em></p>




<img width="922" height="614" alt="image" src="https://github.com/user-attachments/assets/77da70c2-4b6b-4c9a-8cca-089ac72d4a57" />
<p><em>CX View — Customer satisfaction, review trends and critical categories.</em></p>





<img width="916" height="605" alt="image" src="https://github.com/user-attachments/assets/aee7e2b1-40f1-41ea-9309-193585c3dcb6" />
<p><em>Marketplace View — Seller distribution, freight competitiveness and revenue by region.</em></p>




## 👥 Executive Views

### 💰 CFO — Financial Performance

* Total Revenue
* Monthly Revenue Trend
* Average Order Ticket
* Revenue by State

### 🚚 COO — Operational Excellence

* Delivery SLA
* Slowest vs Fastest States
* On-Time Delivery Rate
* Demand by Category

### ⭐ Head of Customer Experience

* Review Score Trend
* Rating Distribution
* Best Categories
* Critical Categories

### 🏪 Head of Marketplace

* Sellers by State
* Seller Revenue Distribution
* Freight Competitiveness
* Partner Ecosystem Health

---

## ⚙️ Tech Stack

| Layer           | Technology |
| --------------- | ---------- |
| Frontend        | Reflex     |
| Backend         | Python     |
| Data Warehouse  | DuckDB     |
| Transformations | dbt        |
| Query Language  | SQL        |
| Dataset         | Olist      |

---

## 🧠 Data Architecture

Raw CSV datasets were transformed into curated business marts using dbt.

### Final Models

```text id="qg3xxj"
mart_financeiro_mensal
mart_logistica_operacional
mart_satisfacao_cliente
mart_desempenho_vendedores
```

These marts were then consumed directly by the Reflex application.

---

## 📂 Project Structure

```bash id="l4vf0s"
volis-dashboard/
│── README.md
│── dashboard_app/
│── olist_project/
│   ├── models/
│   ├── seeds/
│   └── dbt_project.yml
```

---

## 🚀 Run Locally

### Clone Repository

```bash id="6pk8jo"
git clone https://github.com/alecoded/volis-dashboard.git
cd volis-dashboard
```

### Install Dependencies

```bash id="zw4z2r"
pip install -r requirements.txt
```

### Run dbt Models

```bash id="29bxs1"
cd olist_project
dbt seed
dbt run
```

### Start Dashboard

```bash id="g4y75z"
cd ..
reflex run
```

---

## 📈 Executive Impact

This dashboard enables faster and smarter decisions across:

### Revenue Growth

Identify top-performing markets and monetization trends.

### Operational Efficiency

Detect fulfillment bottlenecks and SLA risks.

### Customer Retention

Find poor experiences before they become churn.

### Marketplace Expansion

Optimize seller mix and reduce freight inefficiencies.

---

## 🔥 If Expanded Further

* Predictive revenue forecasting
* Churn risk scoring
* Seller scorecards
* Filters by date / state / category
* CSV / PDF exports
* Cloud deployment
* CI/CD pipeline

---

## 👩‍💻 Author

**Alessandra Lima**
Data Analyst | Data Science | BI

---

## ⭐ Final Note

This project combines analytics, engineering, and product thinking — turning data into executive clarity.

---
