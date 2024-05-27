import pandas as pd
import numpy as np
import os
import locale
import streamlit as st 
import plotly.express as px 
import warnings

warnings.filterwarnings('ignore')
locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')

st.set_page_config(page_title ="report", page_icon=":bar_chart:", layout="wide")
# st.image(r"C:\Users\sunshine\Desktop\project\kalgidhartrustandsocietylogo.gif", use_column_width=True)

#authentication part 

valid_users = {
    "riya": "singla12",
    "harmeet singh": "hsingh00",
    "nandi": "nandi123"
}

def creds_entered():
    username = st.session_state["user"].strip()
    password = st.session_state["passwd"].strip()

    if username in valid_users and valid_users[username] == password:
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        if not password:
            st.warning("Please enter password")
        elif not username:
            st.warning("Please enter username")
        else:
            st.error("Invalid Username/Password")

def authenticate_user():
    if "authenticated" not in st.session_state:
        st.text_input(label="Username:", value="", key="user", on_change=creds_entered)
        st.text_input(label="Password:", value="", key="passwd", type="password", on_change=creds_entered)
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            st.text_input(label="Username:", value="", key="user", on_change=creds_entered)
            st.text_input(label="Password:", value="", key="passwd", type="password", on_change=creds_entered)
            return False
            

if authenticate_user():


        # dashboard code
        st.title(" :bar_chart: Fundraising Dashboard")
        st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True )

        # st.markdown('<style>.block-container {display: flex; justify-content: center; align-items: center; height: 100vh;}</style>', unsafe_allow_html=True)
        # Define the folder path where the default file is located
        default_folder_path = r"C:\Users\sunshine\Desktop\project"
        default_filename = "output.xlsx"

        # File upload functionality
        fl = st.file_uploader(":file_folder: Upload a file", type=(["xlsx", "xls"]))

        # Check if a file is uploaded
        if fl is not None:
            filename = fl.name
            st.write("Uploaded file:", filename)
            df = pd.read_excel(fl)  # Read the uploaded file directly
        else:
            # Check if the default file exists in the specified folder
            if os.path.exists(os.path.join(default_folder_path, default_filename)):
                st.write("Using default file:", default_filename)
                df = pd.read_excel(os.path.join(default_folder_path, default_filename))
            else:
                st.error("Default file not found. Please upload a file first.")
                        
        # Extract start and end dates from "Report Period" column
        df[['Start Date', 'End Date']] = df['Report Period'].str.split(' To ', expand=True)

        # Convert start and end dates to datetime objects
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])

        # User input for start and end dates
        col1, col2 = st.columns(2)
        with col1:
            date1 = st.date_input("Start Date", value=df['Start Date'].min())
        with col2:
            date2 = st.date_input("End Date", value=df['End Date'].max())
        # Convert date inputs to datetime objects
        date1 = pd.Timestamp(date1)
        date2 = pd.Timestamp(date2)

        # Filter the DataFrame based on the selected date range
        df = df[(df['Start Date'] >= date1) & (df['End Date'] <= date2)]
        st.sidebar.header("Choose Your Filter: ")
        Area = st.sidebar.multiselect("Pick your Area",df["Area"].unique())
        if not Area:
            df2 = df.copy()
        else:
            df2 = df[df["Area"].isin(Area)]

        #Create for the Payment_Mode
        # st.sidebar.header("Choose Your Filter: ")
        Payment_Mode = st.sidebar.multiselect("Pick your Payment_Mode",df["Payment_Mode"].unique())
        if not Area:
            df3 = df2.copy()
        else:
            df3 = df2[df2["Area"].isin(Payment_Mode)]

        #run the data based on Area and payment_Mode

        if not Area and not Payment_Mode:
            filtered_df = df
        elif Area and not Payment_Mode:
            filtered_df = df2[df2["Area"].isin(Area)]
        elif not Area and Payment_Mode:
            filtered_df = df2[df2["Payment_Mode"].isin(Payment_Mode)]
        else:
            filtered_df = df2[df2["Area"].isin(Area) & df2["Payment_Mode"].isin(Payment_Mode)]

        # filtered_df['Total Amount'] = filtered_df.apply(lambda row: row['Membership_total'] + row['Child_Sponsorship'] + row['CSR'], axis=1)
        integer_columns = filtered_df.select_dtypes(include=[np.int64, np.float64])

        # Sum the selected integer columns row-wise
        filtered_df['Total Amount'] = integer_columns.sum(axis=1)
        # print(filtered_df)
        with col1:
            st.subheader("Total Amount by Area ")
            fig = px.pie(filtered_df, values="Total Amount", names="Area", hole = 0.5)
            fig.update_traces(text = filtered_df["Area"], textposition = "inside")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Total Payment by Payment Mode")
            fig = px.pie(filtered_df, values="Total Amount", names="Payment_Mode")
            fig.update_traces(textposition = "inside")
            st.plotly_chart(fig, use_container_width=True)

        # Display the KPI
        # st.sidebar.subheader("Total Amount (INR)")
        # st.sidebar.write(total_amount_inr)
        kpi_style = """
            background-color: #074173;
            padding: 10px;
            width: 80%;
            border-radius: 10px;
            color: white;
            text-align: center;
            """

        total_amount = filtered_df['Total Amount'].sum()
        total_amount_inr = locale.currency(total_amount, symbol=True, grouping=True)

        Total_Membership_Amount = filtered_df['Membership_total'].sum()
        total_Membership = locale.currency(Total_Membership_Amount, symbol=True, grouping=True)

        Total_ChildSponsor_Amount = filtered_df['Child_Sponsorship'].sum()
        total_sponsorship = locale.currency(Total_ChildSponsor_Amount, symbol=True, grouping=True)

        Total_CSR_Amount = filtered_df['CSR'].sum()
        total_csr = locale.currency(Total_CSR_Amount, symbol=True, grouping=True)

        # KPI HTML CODE
        kpi_html = f'''
            <div style="{kpi_style}">
            <b>Total Amount</b><br>
            {total_amount_inr}
            <br><br>
            <b>Total Membership Amount</b><br>
            {total_Membership}
            <br><br>
            <b>Total Child Sponsorship Amount</b><br>
            {total_sponsorship}
            <br><br>
            <b>Total Amount of CSR </b><br>
            {total_csr}
            <br><br>
            </div>
            '''

        # Display the HTML in the sidebar
        st.sidebar.markdown(kpi_html, unsafe_allow_html=True)


        # create a treemap based on different Areas

        st.subheader("Amount Recieved by Different Sewa Plans Across Areas")
        # fig2 = px.treemap(filtered_df, path=["Area","Membership_total","Child_Sponsorship","CSR"], values = "Total Amount", hover_data= ["Total Amount"], color="Area")

        # fig2.update_layout(width = 800, height= 650)
        # st.plotly_chart(fig2, use_container_width=True)

        df_selected = df[['Area', 'Membership_total', 'Child_Sponsorship', 'CSR']]

        # Melt the DataFrame to have 'Area' as identifier variable and other columns as measure variables
        melted_df = pd.melt(df_selected, id_vars=['Area'], var_name='Category', value_name='Amount')

        # Convert 'Amount' column to numeric
        melted_df['Amount'] = pd.to_numeric(melted_df['Amount'], errors='coerce')

        # Drop rows with NaN values in the 'Amount' column
        melted_df = melted_df.dropna(subset=['Amount'])

        # # Create the treemap
        melted_df['Area_Category'] = melted_df['Area'] + ' - ' + melted_df['Category']

#tree map created
        fig2 = px.treemap(melted_df, path=['Area', 'Category'], values='Amount', color='Category',
                        color_discrete_map={'Membership_total': '#29b09d','CSR':'#ffd16a','Child_Sponsorship':'#83c9ff'})

        fig2.update_layout(width=800, height=650)
        st.plotly_chart(fig2, use_container_width=True)
        import plotly.figure_factory as ff 

                        # create table chart
                        # st.subheader(":point_right: Amount Recieved by Different Sewa Plans Across Areas")
                        # with st.expander("Total Amount by Area"):
                        #     # Group the DataFrame by 'Area' and calculate the sum of each category
                        #     total_amount_by_area = df.groupby('Area').agg({'Membership_total': 'sum', 
                        #                                                     'Child_Sponsorship': 'sum', 
                        #                                                     'CSR': 'sum'}).reset_index()

                        #     # Create a table with total amount by area and category
                        #     fig = ff.create_table(total_amount_by_area, colorscale="Cividis")
                    #     st.plotly_chart(fig, use_container_width=True)