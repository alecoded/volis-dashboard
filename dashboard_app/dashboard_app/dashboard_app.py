import reflex as rx
import duckdb
import pandas as pd
from datetime import datetime

# 1. Database Connection
def get_query_data(query):
    try:
        conn = duckdb.connect('../olist_project/olist.duckdb')
        df = conn.execute(query).df()
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error: {e}")
        return []

# 2. Professional Category Formatting (English Translation)
def format_categories(data, key):
    exact_corrections = {
        "la_cuisine": "Kitchenware",
        "seguros_e_servicos": "Insurance & Services",
        "informatica_acessorios": "Computers & Accessories",
        "cama_mesa_banho": "Bed, Bath & Table",
        "beleza_saude": "Health & Beauty",
        "esporte_lazer": "Sports & Leisure",
        "moveis_decoracao": "Furniture & Decor",
        "fashion_roupa_infanto_juvenil": "Kids & Teens Fashion",
        "construcao_ferramentas_ferramentas": "Construction Tools",
        "cds_dvds_musicais": "CDs & DVDs",
        "pc_gamer": "PC Gamer",
        "fraldas_higiene": "Diapers & Hygiene",
        "moveis_escritorio": "Office Furniture",
        "sinalizacao_e_seguranca": "Signage & Security",
        "livros_interesse_geral": "General Books",
        "portateis_cozinha_e_preparadores_de_alimentos": "Kitchen Appliances"
    }

    for row in data:
        if row.get(key):
            original_name = str(row[key]).lower()
            if original_name in exact_corrections:
                row[key] = exact_corrections[original_name]
            else:
                # Generic fallback formatting
                generic_name = original_name.replace("_", " ").title()
                generic_name = generic_name.replace(" E ", " & ")
                row[key] = generic_name
    return data

# 3. Date Formatting (English Months)
def format_dates(data, key_value):
    months_en = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', 
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    for i, row in enumerate(data):
        if row.get("month"):
            year, month = str(row["month"]).split("-")
            row["month"] = f"{months_en[month]}-{year}"
        # Skip 1 month for cleaner chart labels
        if i % 2 == 0:
            row[f"label_{key_value}"] = row[key_value]
        else:
            row[f"label_{key_value}"] = ""
    return data

# 4. Thousands Formatting (International Standard: 99,441)
def format_thousands(data, key):
    for row in data:
        if row.get(key) is not None:
            row[f"{key}_formatted"] = f"{int(row[key]):,}"
    return data

# 5. Application State (Business Queries)
class State(rx.State):
    # --- CFO ---
    finance_line: list[dict] = format_dates(get_query_data("""
        SELECT strftime(CAST(mes AS TIMESTAMP), '%Y-%m') as month, round(faturamento_total / 1000000, 2) as total 
        FROM mart_financeiro_mensal 
        WHERE CAST(mes AS TIMESTAMP) >= '2017-01-01' AND CAST(mes AS TIMESTAMP) < '2018-09-01'
        ORDER BY CAST(mes AS TIMESTAMP)
    """), "total")
    
    finance_ticket: list[dict] = format_dates(get_query_data("""
        SELECT strftime(CAST(order_purchase_timestamp AS TIMESTAMP), '%Y-%m') as month, round(avg(payment_value), 2) as ticket 
        FROM olist_orders_dataset o JOIN olist_order_payments_dataset p ON o.order_id = p.order_id 
        WHERE CAST(order_purchase_timestamp AS TIMESTAMP) >= '2017-01-01' AND CAST(order_purchase_timestamp AS TIMESTAMP) < '2018-09-01'
        GROUP BY 1 ORDER BY 1
    """), "ticket")

    finance_states: list[dict] = get_query_data("""
        SELECT c.customer_state as state, round(sum(p.payment_value) / 1000000, 2) as total
        FROM olist_orders_dataset o JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """)

    # --- COO ---
    logistics_sla_piores: list[dict] = get_query_data("""
        SELECT c.customer_state as state, round(avg(date_diff('day', cast(o.order_purchase_timestamp as timestamp), cast(o.order_delivered_customer_date as timestamp))), 1) as days
        FROM olist_orders_dataset o JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        WHERE o.order_delivered_customer_date IS NOT NULL GROUP BY 1 ORDER BY days DESC LIMIT 8
    """)
    
    logistics_sla_melhores: list[dict] = get_query_data("""
        SELECT c.customer_state as state, round(avg(date_diff('day', cast(o.order_purchase_timestamp as timestamp), cast(o.order_delivered_customer_date as timestamp))), 1) as days
        FROM olist_orders_dataset o JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        WHERE o.order_delivered_customer_date IS NOT NULL GROUP BY 1 ORDER BY days ASC LIMIT 8
    """)
    
    logistics_cats_mais: list[dict] = format_thousands(format_categories(get_query_data("""
        SELECT p.product_category_name as category, count(o.order_id) as qty
        FROM olist_orders_dataset o JOIN olist_order_items_dataset i ON o.order_id = i.order_id
        JOIN olist_products_dataset p ON i.product_id = p.product_id
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """), "category"), "qty")
    
    logistics_cats_menos: list[dict] = format_thousands(format_categories(get_query_data("""
        SELECT p.product_category_name as category, count(o.order_id) as qty
        FROM olist_orders_dataset o JOIN olist_order_items_dataset i ON o.order_id = i.order_id
        JOIN olist_products_dataset p ON i.product_id = p.product_id
        GROUP BY 1 ORDER BY 2 ASC LIMIT 5
    """), "category"), "qty")
    
    logistics_pontualidade: list[dict] = format_thousands(get_query_data("""
        SELECT 
            CASE 
                WHEN order_delivered_customer_date IS NULL THEN 'Canceled / Lost'
                WHEN cast(order_delivered_customer_date as date) > cast(order_estimated_delivery_date as date) THEN 'Delayed' 
                ELSE 'On Time' 
            END as status, 
            count(order_id) as qty 
        FROM olist_orders_dataset 
        GROUP BY 1 ORDER BY qty DESC
    """), "qty")

    # --- CX ---
    cx_evolucao: list[dict] = format_dates(get_query_data("""
        SELECT strftime(CAST(review_creation_date AS TIMESTAMP), '%Y-%m') as month, round(avg(review_score), 2) as score 
        FROM olist_order_reviews_dataset 
        WHERE CAST(review_creation_date AS TIMESTAMP) >= '2017-01-01' AND CAST(review_creation_date AS TIMESTAMP) < '2018-09-01'
        GROUP BY 1 ORDER BY 1
    """), "score")
    
    cx_distribuicao: list[dict] = format_thousands(get_query_data("""
        SELECT 
            CAST(review_score AS VARCHAR) || ' Stars' as score_label, 
            CAST(COUNT(review_id) AS INTEGER) as qty
        FROM olist_order_reviews_dataset 
        WHERE review_score IS NOT NULL 
        GROUP BY review_score 
        ORDER BY review_score ASC
    """), "qty")

    # CORREÇÃO AQUI: product_category_name em vez de cat
    cx_top: list[dict] = format_categories(get_query_data("""
        SELECT product_category_name as category, round(nota_media, 2) as score 
        FROM mart_satisfacao_cliente WHERE product_category_name IS NOT NULL ORDER BY score DESC LIMIT 5
    """), "category")
    
    # CORREÇÃO AQUI: product_category_name em vez de cat
    cx_piores: list[dict] = format_categories(get_query_data("""
        SELECT product_category_name as category, round(nota_media, 2) as score 
        FROM mart_satisfacao_cliente WHERE product_category_name IS NOT NULL ORDER BY score ASC LIMIT 5
    """), "category")

    # --- MARKETPLACE ---
    mkt_sellers_estado: list[dict] = format_thousands(get_query_data("""
        SELECT seller_state as state, count(seller_id) as qty
        FROM olist_sellers_dataset
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """), "qty")

    mkt_receita_estado: list[dict] = get_query_data("""
        SELECT s.seller_state as state, round(sum(i.price)/1000000, 2) as total
        FROM olist_order_items_dataset i
        JOIN olist_sellers_dataset s ON i.seller_id = s.seller_id
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5
    """)

    mkt_frete_estado: list[dict] = get_query_data("""
        SELECT s.seller_state as state, round(avg(i.freight_value), 2) as freight
        FROM olist_order_items_dataset i
        JOIN olist_sellers_dataset s ON i.seller_id = s.seller_id
        GROUP BY 1 ORDER BY 2 DESC LIMIT 8
    """)


# 6. Reusable UI Components
def mini_kpi(icon_tag, label, value, color, subtitle):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag=icon_tag, size=16, color=rx.color(color, 11)),
                rx.text(label, font_size="0.8em", font_weight="bold", color_scheme="gray", margin="0"),
                align_items="center", spacing="2"
            ),
            rx.heading(value, size="7", color_scheme=color, margin="0", padding_y="0.1em"),
            rx.text(subtitle, font_size="0.65em", color_scheme="gray", margin="0"),
            spacing="1", align_items="start",
        ),
        padding="1.2em 1.5em", border_radius="10px", border=f"1px solid {rx.color('gray', 4)}", background_color="white", width="100%",
        box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    )

def big_chart_card(title, subtitle, chart, height="300px"):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(rx.heading(title, size="4"), rx.text(subtitle, size="2", color_scheme="gray"), align_items="start"),
                rx.spacer(), width="100%"
            ),
            rx.box(chart, width="100%", padding_top="1em", height=height),
        ),
        padding="1.5em", border_radius="15px", background_color="white", width="100%", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)"
    )

# 7. Main Dashboard Interface
def index() -> rx.Component:
    return rx.box( 
        rx.box( 
            rx.vstack(
                # Header
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Olist", size="8", font_weight="black", color_scheme="indigo"),
                            rx.heading("| Strategic Intelligence", size="8", font_weight="light"),
                            spacing="2"
                        ),
                        rx.hstack(
                            rx.badge("Analysis Period: Jan/2017 to Aug/2018", variant="outline", color_scheme="gray"),
                            rx.badge("Real-time updates", variant="soft", color_scheme="green"),
                            spacing="2"
                        ),
                        align_items="start", spacing="1"
                    ),
                    rx.spacer(),
                    rx.badge("Currency: BRL (R$)", variant="surface", size="3", color_scheme="indigo"),
                    width="100%", padding_bottom="1.5em"
                ),
                
                # Main Top KPIs
                rx.grid(
                    mini_kpi("dollar-sign", "Total Revenue", "R$ 15.8M", "green", "Accumulated gross revenue"),
                    mini_kpi("shopping-bag", "Order Volume", "99,441", "blue", "Total purchases completed"),
                    mini_kpi("credit-card", "Average Ticket", "R$ 159", "purple", "Average spend per transaction"),
                    mini_kpi("clock", "Average SLA", "12.5 Days", "red", "Average delivery time"),
                    columns="4", spacing="4", width="100%",
                ),

                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger(rx.hstack(rx.icon("wallet", size=18), rx.text("Financial (CFO)"), align_items="center", spacing="2"), value="cfo"),
                        rx.tabs.trigger(rx.hstack(rx.icon("truck", size=18), rx.text("Operations (COO)"), align_items="center", spacing="2"), value="coo"),
                        rx.tabs.trigger(rx.hstack(rx.icon("star", size=18), rx.text("Customer Experience (CX)"), align_items="center", spacing="2"), value="cx"),
                        rx.tabs.trigger(rx.hstack(rx.icon("store", size=18), rx.text("Marketplace"), align_items="center", spacing="2"), value="mkt"),
                    ),
                    
                    # --- CFO TAB ---
                    rx.tabs.content(
                        rx.vstack(
                            big_chart_card("Monthly Revenue (Millions)", "Historical cash flow analysis",
                                rx.recharts.line_chart(
                                    rx.recharts.line(
                                        rx.recharts.label_list(data_key="label_total", position="top", font_size=12, fill="#10b981"),
                                        data_key="total", type="monotone", stroke="#10b981", stroke_width=3, dot=True
                                    ),
                                    rx.recharts.x_axis(data_key="month", interval=1, font_size=12, angle=-20, text_anchor="end", height=50), 
                                    rx.recharts.y_axis(font_size=12),
                                    rx.recharts.graphing_tooltip(), data=State.finance_line, width="100%", height=320
                                )
                            ),
                            rx.grid(
                                big_chart_card("Average Ticket per Month", "Evolution of customer spend per order",
                                    rx.recharts.area_chart(
                                        rx.recharts.area(
                                            rx.recharts.label_list(data_key="label_ticket", position="top", font_size=12, fill="#6d28d9"),
                                            data_key="ticket", fill="#8b5cf6", stroke="#6d28d9", opacity=0.3
                                        ),
                                        rx.recharts.x_axis(data_key="month", interval=1, font_size=12, angle=-20, text_anchor="end", height=50), 
                                        rx.recharts.y_axis(domain=[100, 180], font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.finance_ticket, width="100%", height=250
                                    ), height="280px"
                                ),
                                big_chart_card("Revenue by State (Top 5)", "Customer regions with highest revenue volume (Millions)",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="total", position="top", font_size=12), data_key="total", fill="#10b981", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.finance_states, width="100%", height=250
                                    ), height="280px"
                                ),
                                columns="2", spacing="6", width="100%", margin_top="1.5em"
                            ),
                            spacing="6", width="100%", margin_top="1.5em"
                        ), value="cfo",
                    ),

                    # --- COO TAB ---
                    rx.tabs.content(
                        rx.vstack(
                            rx.grid(
                                big_chart_card("Logistics Bottlenecks (Slowest)", "States with longest delivery lead times",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="days", position="top", font_size=12), data_key="days", fill="#ef4444", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.logistics_sla_piores, width="100%", height=250
                                    ), height="280px"
                                ),
                                big_chart_card("Operational Efficiency (Fastest)", "States with best delivery performance",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="days", position="top", font_size=12), data_key="days", fill="#10b981", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.logistics_sla_melhores, width="100%", height=250
                                    ), height="280px"
                                ),
                                columns="2", spacing="6", width="100%"
                            ),
                            rx.grid(
                                big_chart_card("Low Traction Products", "Categories with lowest sales volume",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="qty_formatted", position="top", font_size=11), data_key="qty", fill="#64748b", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="category", angle=-25, text_anchor="end", height=100, font_size=11), rx.recharts.y_axis(font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.logistics_cats_menos, width="100%", height=240
                                    ), height="280px"
                                ),
                                big_chart_card("High Demand Products", "Categories with highest sales volume",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="qty_formatted", position="top", font_size=11), data_key="qty", fill="#3b82f6", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="category", angle=-25, text_anchor="end", height=100, font_size=11), rx.recharts.y_axis(font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.logistics_cats_mais, width="100%", height=240
                                    ), height="280px"
                                ),
                                columns="2", spacing="6", width="100%", margin_top="1.5em"
                            ),
                            rx.grid(
                                big_chart_card("Overall On-Time Delivery Rate", "Delivery status across the entire order funnel",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="qty_formatted", position="top", font_size=12), data_key="qty", fill="#8b5cf6", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="status", font_size=12), rx.recharts.y_axis(font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.logistics_pontualidade, width="100%", height=240
                                    ), height="280px"
                                ),
                                columns="1", width="100%", margin_top="1.5em"
                            ),
                            spacing="6", width="100%", margin_top="1.5em"
                        ), value="coo",
                    ),

                    # --- CX TAB ---
                    rx.tabs.content(
                        rx.vstack(
                            rx.grid(
                                big_chart_card("Customer Satisfaction (CSAT)", "Monthly evolution of the average review score",
                                    rx.recharts.line_chart(
                                        rx.recharts.line(
                                            rx.recharts.label_list(data_key="label_score", position="top", font_size=12, fill="#f59e0b"),
                                            data_key="score", type="monotone", stroke="#f59e0b", stroke_width=3, dot=True
                                        ),
                                        rx.recharts.x_axis(data_key="month", interval=1, font_size=12, angle=-20, text_anchor="end", height=50), 
                                        rx.recharts.y_axis(domain=[3.5, 4.5], font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.cx_evolucao, width="100%", height=280
                                    ), height="300px"
                                ),
                                big_chart_card("Review Score Distribution", "Total volume of reviews by star rating",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="qty_formatted", position="top", font_size=11), data_key="qty", fill="#f59e0b", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="score_label", font_size=11), 
                                        rx.recharts.y_axis(font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.cx_distribuicao, width="100%", height=240
                                    ), height="300px"
                                ),
                                columns="2", spacing="6", width="100%"
                            ),
                            rx.grid(
                                big_chart_card("Top 5 Categories (Stars)", "Categories with the best customer feedback",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="score", position="top", font_size=12), data_key="score", fill="#10b981", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="category", angle=-25, text_anchor="end", height=100, font_size=11), rx.recharts.y_axis(domain=[3.5, 5], font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.cx_top, width="100%", height=240
                                    ), height="280px"
                                ),
                                big_chart_card("Bottom 5 Categories (Critical)", "Areas requiring intervention to improve NPS",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="score", position="top", font_size=12), data_key="score", fill="#ef4444", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="category", angle=-25, text_anchor="end", height=100, font_size=11), rx.recharts.y_axis(domain=[1, 4], font_size=11),
                                        rx.recharts.graphing_tooltip(), data=State.cx_piores, width="100%", height=240
                                    ), height="280px"
                                ),
                                columns="2", spacing="6", width="100%", margin_top="1.5em"
                            ),
                            spacing="6", width="100%", margin_top="1.5em"
                        ), value="cx",
                    ),

                    # --- MARKETPLACE TAB ---
                    rx.tabs.content(
                        rx.vstack(
                            rx.grid(
                                big_chart_card("Seller Concentration", "Volume of partner sellers by state",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="qty_formatted", position="top", font_size=12), data_key="qty", fill="#3b82f6", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.mkt_sellers_estado, width="100%", height=240
                                    ), height="280px"
                                ),
                                big_chart_card("Revenue Generated by State (Seller)", "Total revenue originated by partners (Millions)",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="total", position="top", font_size=12), data_key="total", fill="#10b981", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.mkt_receita_estado, width="100%", height=240
                                    ), height="280px"
                                ),
                                columns="2", spacing="6", width="100%"
                            ),
                            rx.grid(
                                big_chart_card("Freight Competitiveness", "Average freight cost charged based on seller's state (R$)",
                                    rx.recharts.bar_chart(
                                        rx.recharts.bar(rx.recharts.label_list(data_key="freight", position="top", font_size=12), data_key="freight", fill="#f59e0b", radius=[4, 4, 0, 0]),
                                        rx.recharts.x_axis(data_key="state", font_size=12), rx.recharts.y_axis(font_size=12),
                                        rx.recharts.graphing_tooltip(), data=State.mkt_frete_estado, width="100%", height=240
                                    ), height="280px"
                                ),
                                columns="1", width="100%", margin_top="1.5em"
                            ),
                            spacing="6", width="100%", margin_top="1.5em"
                        ), value="mkt",
                    ),
                    width="100%",
                ),
                
                # Footer
                rx.divider(margin_top="3em", margin_bottom="1em"),
                rx.hstack(
                    rx.text("Data Source: Olist Public Dataset", size="2", color_scheme="gray"),
                    rx.spacer(),
                    rx.text(f"Generated on: {datetime.now().strftime('%Y-%m-%d')} | Classification: Restricted", size="2", color_scheme="gray"),
                    width="100%",
                    padding_bottom="2em"
                ),
                
                spacing="5", width="100%",
            ),
            width="100%", 
            max_width="1500px", 
            margin="0 auto", 
            padding_x=["1em", "2em", "3em"],
            padding_y="2em",
        ),
        background_color="#E5E7EB",
        min_height="100vh",
        width="100%",
    )

app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index)