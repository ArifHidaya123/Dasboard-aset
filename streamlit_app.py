import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

#######################################
# NEWS PAGE
#######################################

def show_news_page(df):
    st.title("Distribusi Aset PT.PLN UP3 Surabaya Barat")

    # Sidebar filter for BULAN
    bulan_options = df['BULAN'].dropna().unique().tolist() 
    selected_bulan = st.sidebar.selectbox("Select month", bulan_options)

    # Filter the dataframe by the selected BULAN
    filtered_df = df[df['BULAN'] == selected_bulan]

    # Displaying pie charts for selected assets
    def plot_pie_chart_for_asset(filtered_df, asset):
        asset_data = filtered_df[filtered_df['ASET'] == asset]
        if asset_data.empty:
            return None

        persen = asset_data['PERSEN'].values[0]
        sisa_persen = asset_data['SISA PERSENTASE'].values[0]

        # Handle cases where PERSEN is greater than 100%
        if persen > 100:
            sisa_persen = 0
            persen = 100
        elif persen < 0:
            sisa_persen = 100
            persen = 0

        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=['PERSEN', 'SISA PERSENTASE'],
            values=[persen, sisa_persen],
            name=asset,
            marker=dict(colors=['#1f77b4', '#2ca02c'])  # Set colors here
        ))

        fig.update_layout(
            title_text=f'PERSEN and SISA PERSENTASE for Asset: {asset}',
            showlegend=True
        )

        return fig

    # Display bar charts for selected assets
    def plot_bar_chart_for_asset(filtered_df, asset):
        asset_data = filtered_df[filtered_df['ASET'] == asset]
        if asset_data.empty:
            return None

        fig = go.Figure(data=[
            go.Bar(name='MAXIMO', y=[f"{asset} "], x=[asset_data['MAXIMO'].values[0]], marker_color='#1f77b4', orientation='h'),
            go.Bar(name='LTB', y=[f"{asset}  "], x=[asset_data['LTB '].values[0]], marker_color='#2ca02c', orientation='h')
        ])

        fig.update_layout(
            barmode='group',
            title_text=f'MAXIMO and LTB for Asset: {asset}',
            xaxis_title="Value",
            yaxis_title="Asset",
            height=400,  # Adjust the height of the chart
            bargap=0.2,  # Add spacing between bars
            yaxis=dict(tickmode='array', tickvals=[f"{asset} ", f"{asset}  "], ticktext=[asset, '']),
            yaxis2=dict(tickvals=[f"{asset}  "], overlaying='y', side='right')
        )

        return fig

    # Get unique assets from the dataframe
    assets_to_display = df['ASET'].unique().tolist()

    # Display the pie charts and bar charts for each asset
    for asset in assets_to_display:
        filtered_by_asset = filtered_df[filtered_df['ASET'] == asset]
        if not filtered_by_asset.empty:
            col1, col2, col3 = st.columns(3)

            with col1:
                pie_chart_fig = plot_pie_chart_for_asset(filtered_by_asset, asset)
                st.plotly_chart(pie_chart_fig, use_container_width=True)

            with col2:
                bar_chart_fig = plot_bar_chart_for_asset(filtered_by_asset, asset)
                st.plotly_chart(bar_chart_fig, use_container_width=True)

            with col3:
                st.subheader(f"Total GAP for Asset: {asset}")
                total_gap = filtered_by_asset['GAP'].sum()
                formatted_gap = "{:,.0f}".format(total_gap)  # Format GAP to thousand separator
                st.write(f"Total GAP: {formatted_gap}")


#######################################
# MAIN APP
#######################################

# Set page configuration
st.set_page_config(
    page_title="Asset Dashboard",
    page_icon="::",
    layout="wide",
    initial_sidebar_state="expanded"  # Expanded sidebar by default
)

# Custom CSS for background gradient and navbar
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #ffffff, #b3d9ff);  /* Blue to white gradient */
    }

    .navbar {
        background-color: grey;
        padding: 10px;
        border: 3px solid purple;
        border-radius: 5px;
        margin-bottom: 20px;
        transition-duration: 0.4s;
    }

    .navbar a {
        text-decoration: none;
        color: white;
        padding: 5px 15px;
        margin-right: 10px;
        border-radius: 3px;
    }

    .navbar a:hover {
        background-color: black;
        color: grey;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar setup
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "xls"])

# Stop execution if no file is uploaded
if uploaded_file is None:
    st.info("Upload a file", icon="ℹ")
    st.stop()

#######################################
# DATA LOADING
#######################################

@st.cache
def load_data(path: str):
    file_extension = path.name.split('.')[-1]
    if file_extension == 'xlsx':
        df = pd.read_excel(path, engine='openpyxl')
    elif file_extension == 'xls':
        df = pd.read_excel(path, engine='xlrd')
    else:
        st.error("Unsupported file type")
        return None
    return df

df = load_data(uploaded_file)

if df is None:
    st.stop()

#######################################
# FILTER SETUP
#######################################

# Display the navbar using st.markdown
navbar_html = """
<div class="navbar">
    <a href="?page=Home">Home</a>
    <a href="?page=News">Distribusi Aset</a> 
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# Determine the selected page
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["Home"])[0]

# Extract month from Changed Date
df['Changed Date'] = pd.to_datetime(df['Changed Date'])
df['Changed Month'] = df['Changed Date'].dt.strftime('%B')

if page == "Home":
    # Sidebar filters
    status_options = df['Status'].unique().tolist()
    selected_status = st.sidebar.multiselect("Select Status", status_options, default=status_options)

    # Sidebar filter for months (multiple selection)
    bulan_options = df['Changed Month'].dropna().unique().tolist()  # Drop NaN values
    selected_months = st.sidebar.multiselect("Select Months", bulan_options, default=bulan_options)

    # Filter dataframe based on selected filters
    filtered_df = df[df['Status'].isin(selected_status) & df['Changed Month'].isin(selected_months)]

    # Sidebar filter for BULAN (multiple selection)
    bulan_options = df['BULAN'].dropna().unique().tolist()  # Drop NaN values
    selected_bulan = st.sidebar.multiselect("Select month", bulan_options, default=bulan_options)

    # Filter the dataframe by the selected BULAN
    filtered_bulan_df = df[df['BULAN'].isin(selected_bulan)]

    #######################################
    # VISUALIZATION METHODS
    #######################################

    def plot_class_description(filtered_df):
        class_description_data = filtered_df.groupby("Class Description").size().reset_index(name="count")
        class_description_data = class_description_data.sort_values(by="count", ascending=False)

        fig = px.bar(
            class_description_data,
            x="Class Description",
            y="count",
            text="count",  # Add text on top of each bar
            title="Count of Assets by Class Description",
            height=400,
            color_discrete_sequence=['#1f77b4'] * len(class_description_data)  # Set color to #1f77b4
        )

        fig.update_traces(
            textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
        )
        fig.update_layout(
            xaxis_title="Class Description",
            yaxis_title="Count",
        )
        return fig

    def plot_total_assets(filtered_df):
        total_assets = len(filtered_df)  # Calculate total rows in DataFrame as total assets
        st.metric("Total Assets", total_assets)

    def plot_status_counts(filtered_df):
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'count']

        col1, col2, col3 = st.columns(3)
        for index, row in status_counts.iterrows():
            col1.metric(row['Status'], row['count'])

    def plot_bar_charts_for_selected_months(filtered_bulan_df, asset):
        asset_data = filtered_bulan_df[filtered_bulan_df['ASET'] == asset]
        if asset_data.empty:
            st.warning(f"No data available for asset: {asset}")
            return None

        # Create subplots for each month
        num_months = len(selected_bulan)
        fig = make_subplots(
            rows=1, cols=num_months,
            subplot_titles=selected_bulan,
            shared_yaxes=True
        )

        for i, bulan in enumerate(selected_bulan):
            bulan_data = asset_data[asset_data['BULAN'] == bulan]
            if not bulan_data.empty:
                fig.add_trace(
                    go.Bar(
                        x=['MAXIMO', 'LTB '],
                        y=[bulan_data['MAXIMO'].values[0], bulan_data['LTB '].values[0]],
                        name=bulan,
                        marker_color=['#1f77b4', '#2ca02c'],
                        width=0.4  # Adjust width of the bars here
                    ),
                    row=1, col=i+1
                )

        fig.update_layout(
            title_text=f'MAXIMO and LTB for Asset: {asset}',
            xaxis_title="Category",
            yaxis_title="Value",
            height=400,  # Adjust the height of the chart
            bargap=0.3,  # Add spacing between bars
            bargroupgap=0.2,  # Add spacing between groups of bars
            showlegend=False
        )

        return fig


    def plot_growth_graph(filtered_bulan_df, asset):
        asset_data = filtered_bulan_df[filtered_bulan_df['ASET'] == asset]
        if asset_data.empty:
            st.warning(f"No data available for asset: {asset}")
            return None

        # Convert BULAN to datetime with a default year
        asset_data['BULAN'] = pd.to_datetime(asset_data['BULAN'] + ' 2024', format='%B %Y')

        # Sort data by BULAN
        asset_data = asset_data.sort_values(by='BULAN')

        fig = go.Figure()

        # Plot MAXIMO
        fig.add_trace(go.Scatter(
            x=asset_data['BULAN'],
            y=asset_data['MAXIMO'],
            mode='lines+markers',
            name='MAXIMO',
            line=dict(color='#1f77b4', width=2)
        ))

        # Plot LTB
        fig.add_trace(go.Scatter(
            x=asset_data['BULAN'],
            y=asset_data['LTB '],
            mode='lines+markers',
            name='LTB ',
            line=dict(color='#2ca02c', width=2)
        ))

        fig.update_layout(
            title_text=f'Growth of MAXIMO and LTB for Asset: {asset}',
            xaxis_title="Month",
            yaxis_title="Value",
            height=400,  # Adjust the height of the chart
            xaxis=dict(
                tickmode='array',
                tickvals=asset_data['BULAN'],
                ticktext=[date.strftime('%b %Y') for date in asset_data['BULAN']]
            )
        )

        return fig


    #######################################
    # STREAMLIT LAYOUT
    #######################################

    # Create two columns
    col1, col2 = st.columns([2, 1])

    # Display the Class Description chart in the first column
    with col1:
        if not filtered_df.empty:
            st.plotly_chart(plot_class_description(filtered_df), use_container_width=True)

    # Display the total assets and status counts in the second column
    with col2:
        if not filtered_df.empty:
            plot_total_assets(filtered_df)
            plot_status_counts(filtered_df)

    # Dropdown to select an asset
    selected_asset = st.selectbox("Select an Asset", filtered_bulan_df['ASET'].unique())

    # Display the bar charts and growth graph for selected assets
    filtered_by_asset = filtered_bulan_df[filtered_bulan_df['ASET'] == selected_asset]
    if not filtered_by_asset.empty:
        bar_chart_fig = plot_bar_charts_for_selected_months(filtered_by_asset, selected_asset)
        st.plotly_chart(bar_chart_fig, use_container_width=True)
        
        # Display growth graph
        growth_graph_fig = plot_growth_graph(filtered_bulan_df, selected_asset)
        st.plotly_chart(growth_graph_fig, use_container_width=True)
    else:
        st.warning(f"No data available for asset: {selected_asset}")

elif page == "News":
    show_news_page(df)  # Call the function directly here
