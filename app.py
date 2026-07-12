import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


st.set_page_config(
    page_title="E-Commerce Business Dashboard",
    layout="wide"
)

st.title("📊 E-Commerce Business Dashboard")
st.markdown("Business Performance Analysis")

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("C:\python\data.csv", encoding="ISO-8859-1")

    # Remove missing CustomerID
    df = df.dropna(subset=["CustomerID"])

    # Remove cancelled orders
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    # Remove negative values
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    # Convert date
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Revenue
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    # Year & Month
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.strftime("%B")

    

    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

country = st.sidebar.multiselect(
    "Country",
    options=sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

year = st.sidebar.multiselect(
    "Year",
    options=sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

filtered_df = df[
    (df["Country"].isin(country)) &
    (df["Year"].isin(year))
]

# Customer Spending
customer_value = (
    filtered_df.groupby("CustomerID")["Revenue"]
    .sum()
    .reset_index()
)

# Customer Segments
customer_value["Segment"] = pd.cut(
    customer_value["Revenue"],
    bins=[0,100,500,1500,customer_value["Revenue"].max()+1],
    labels=[
        "Low (<£100)",
        "Medium (£100-500)",
        "High (£500-1.5k)",
        "VIP (£1.5k+)"
    ]
)

# -----------------------------
# KPIs
# -----------------------------
total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["InvoiceNo"].nunique()
total_customers = filtered_df["CustomerID"].nunique()
avg_order = total_revenue / total_orders

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
c2.metric("🛒 Total Orders", total_orders)
c3.metric("👥 Customers", total_customers)
c4.metric("📦 Avg Order Value", f"${avg_order:,.2f}")
# -----------------------------
# Dashboard Charts
# -----------------------------

col1, col2 = st.columns(2)

# =============================
# Revenue Trend
# =============================
with col1:

    monthly = filtered_df.groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["Revenue"].sum().reset_index()

    monthly["InvoiceDate"] = monthly["InvoiceDate"].astype(str)

    fig = px.line(
        monthly,
        x="InvoiceDate",
        y="Revenue",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=["#25A4F2"]
    )

    fig.update_layout(
        title="Revenue Trend Over Time",
        height=420
    )

    st.plotly_chart(fig, use_container_width=True)

# =============================
# Top Countries
# =============================
with col2:

    country = filtered_df.groupby("Country")["Revenue"].sum().nlargest(10).reset_index()

    fig = px.bar(
        country,
        x="Revenue",
        y="Country",
        orientation="h",
        template="plotly_dark",
        color_discrete_sequence=["#184EA6"]
    )

    fig.update_layout(
        title="Top 10 Countries by Revenue",
        height=420
    )

    fig.update_yaxes(categoryorder="total ascending")

    st.plotly_chart(fig, use_container_width=True)

############################################################

col3, col4 = st.columns(2)

# =============================
# Top Products
# =============================
with col3:

    products = filtered_df.groupby("Description")["Revenue"].sum().nlargest(10).reset_index()

    fig = px.bar(
        products,
        x="Revenue",
        y="Description",
        orientation="h",
        template="plotly_dark",
        color="Revenue",
        color_continuous_scale="Greens"
    )

    fig.update_layout(
        title="Top 10 Products by Revenue",
        height=420,
        coloraxis_showscale=False
    )

    fig.update_yaxes(categoryorder="total ascending")

    st.plotly_chart(fig, use_container_width=True)

# =============================
# Top Customers
# =============================
with col4:

    segment_count = (
        customer_value["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_count.columns = ["Segment","Customers"]

    fig = px.pie(
        segment_count,
        names="Segment",
        values="Customers",
        hole=0.45,
        template="plotly_dark",
        color_discrete_sequence=[
            "#4B0082",
            "#6A5ACD",
            "#9370DB",
            "#C4B5FD"
        ]
    )

    fig.update_layout(
        title="Customer Value Segments",
        height=420
    )

    st.plotly_chart(fig,use_container_width=True)



st.markdown("---")

st.subheader("Revenue vs Quantity")

sample = filtered_df.sample(
    min(4000,len(filtered_df)),
    random_state=42
)

fig = px.scatter(
    sample,
    x="Quantity",
    y="Revenue",
    color="Country",
    template="plotly_dark",
    opacity=0.7,
    title="Relationship Between Quantity and Revenue"
)

fig.update_layout(
    height=550
)

st.plotly_chart(fig,use_container_width=True)
# -----------------------------
# Business Recommendations
# -----------------------------
st.subheader("💡 Business Recommendations")

top_country_name = (
    filtered_df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

top_product_name = (
    filtered_df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

highest_month = (
    filtered_df.groupby(filtered_df["InvoiceDate"].dt.month_name())["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

st.success(f"""
### Key Business Insights

✅ **Highest Revenue Country:** {top_country_name}

➡ Focus marketing campaigns and inventory planning in this country.

---

✅ **Best Selling Product:** {top_product_name}

➡ Maintain sufficient stock and promote this product through offers.

---

✅ **Highest Sales Month:** {highest_month}

➡ Increase inventory, advertisements and staffing before this month.

---

✅ Customer Retention

➡ Introduce loyalty programs and personalized discounts for repeat customers.

---

✅ Inventory Management

➡ Monitor slow-moving products and optimize stock levels to reduce storage costs.
""")

# -----------------------------
# Download Filtered Dataset
# -----------------------------
st.subheader("⬇ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_ecommerce_data.csv",
    mime="text/csv"
)

# -----------------------------
# Dashboard Footer
# -----------------------------
st.markdown("---")
st.markdown(
    """
### 📌 Dashboard Summary

This dashboard provides interactive business insights using the Online Retail dataset.

**KPIs**
- Total Revenue
- Total Orders
- Total Customers
- Average Order Value

**Visualizations**
- Monthly Revenue Trend
- Top 10 Products
- Top 10 Countries
- Top 10 Customers

**Features**
- Interactive Country Filter
- Interactive Year Filter
- Download Filtered Data
- Business Recommendations
"""
)

st.caption("Developed using Python, Pandas, Matplotlib and Streamlit")